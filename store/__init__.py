from __future__ import annotations

import json
import os
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from contracts.errors import ScopeError


@dataclass
class Scope:
    role: str
    allowed_projects: list[str] = field(default_factory=list)
    allowed_tags: list[str] = field(default_factory=list)
    visibility: str = "project"


_DEFAULT_DB_PATH = os.getenv("DP_DB_PATH", os.path.join("var", "decisionprint.db"))
_CURRENT_DB_PATH = _DEFAULT_DB_PATH


def _active_db_path() -> str:
    return os.getenv("DP_DB_PATH", _CURRENT_DB_PATH or _DEFAULT_DB_PATH)


def _ensure_parent(path: str) -> None:
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)


def _schema_tables() -> set[str]:
    return {
        "projects",
        "sources",
        "decisions",
        "decision_constraints",
        "decision_evidence",
        "outcomes",
        "audit_events",
        "project_context",
        "causal_links",
    }


def _connect(db_path: str | None = None) -> sqlite3.Connection:
    global _CURRENT_DB_PATH
    target = db_path or _active_db_path()
    _CURRENT_DB_PATH = target
    _ensure_parent(target)
    connection = sqlite3.connect(target)
    connection.row_factory = sqlite3.Row
    _ensure_schema(connection)
    return connection


def _ensure_schema(conn: sqlite3.Connection) -> None:
    existing = {
        row[0]
        for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    }
    if existing.issuperset(_schema_tables()):
        return

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS projects (
            project_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS sources (
            source_id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL,
            source_type TEXT,
            title TEXT,
            hindsight_document_id TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(project_id) REFERENCES projects(project_id)
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS decisions (
            decision_id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL,
            title TEXT,
            decision_statement TEXT,
            occurred_at TEXT,
            status TEXT NOT NULL DEFAULT 'active',
            superseded_by TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(project_id) REFERENCES projects(project_id)
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS decision_constraints (
            constraint_id TEXT PRIMARY KEY,
            decision_id TEXT NOT NULL,
            name TEXT NOT NULL,
            value TEXT,
            unit TEXT,
            source_memory_id TEXT,
            FOREIGN KEY(decision_id) REFERENCES decisions(decision_id)
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS decision_evidence (
            evidence_id TEXT PRIMARY KEY,
            decision_id TEXT NOT NULL,
            source_id TEXT,
            source_memory_id TEXT,
            summary TEXT,
            FOREIGN KEY(decision_id) REFERENCES decisions(decision_id)
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS outcomes (
            outcome_id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL,
            decision_id TEXT,
            title TEXT,
            summary TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(project_id) REFERENCES projects(project_id)
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS audit_events (
            event_id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            action TEXT NOT NULL,
            role TEXT NOT NULL,
            project_id TEXT,
            query_id TEXT,
            decision_ids TEXT,
            output_hash TEXT,
            recalled_memory_ids TEXT,
            scope_json TEXT,
            actor TEXT
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS project_context (
            project_id TEXT PRIMARY KEY,
            consumer_count INTEGER,
            replay_required INTEGER,
            current_project TEXT,
            context_json TEXT,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(project_id) REFERENCES projects(project_id)
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS causal_links (
            causal_link_id TEXT PRIMARY KEY,
            decision_id TEXT NOT NULL,
            outcome_id TEXT,
            relation TEXT,
            evidence_ids TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(decision_id) REFERENCES decisions(decision_id)
        )
        """
    )
    conn.commit()


def init_database(db_path: str | None = None) -> None:
    """Create the core SQLite tables used by DecisionPrint and make them idempotent."""
    global _CURRENT_DB_PATH
    target = db_path or _active_db_path()
    _CURRENT_DB_PATH = target
    conn = _connect(target)
    try:
        _ensure_schema(conn)
    finally:
        conn.close()


def _now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _serialize_json(value: Any) -> str:
    return json.dumps(value, default=str)


def _deserialize_json(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value
    return value


def upsert_project(project_id: str, name: str, *, description: str | None = None) -> dict[str, Any]:
    conn = _connect()
    try:
        now = _now_utc()
        conn.execute(
            """
            INSERT INTO projects(project_id, name, description, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(project_id)
            DO UPDATE SET name = excluded.name,
                          description = excluded.description,
                          updated_at = excluded.updated_at
            """,
            (project_id, name, description, now, now),
        )
        conn.commit()
        return get_project(project_id)
    finally:
        conn.close()


def get_project(project_id: str) -> dict[str, Any]:
    conn = _connect()
    try:
        row = conn.execute(
            "SELECT project_id, name, description, created_at, updated_at FROM projects WHERE project_id = ?",
            (project_id,),
        ).fetchone()
        if row is None:
            raise KeyError(project_id)
        return dict(row)
    finally:
        conn.close()


def list_projects_in_scope(scope: Scope) -> list[str]:
    conn = _connect()
    try:
        rows = conn.execute("SELECT project_id FROM projects ORDER BY project_id").fetchall()
        projects = [row["project_id"] for row in rows]
        if scope.role == "engineer":
            projects = [project_id for project_id in projects if project_id.lower() != "delta"]
        if not scope.allowed_projects:
            return projects
        return [project_id for project_id in projects if project_id in set(scope.allowed_projects)]
    finally:
        conn.close()


def list_project_records(scope: Scope) -> list[dict[str, Any]]:
    project_ids = list_projects_in_scope(scope)
    return [get_project(project_id) for project_id in project_ids]


def list_source_records(*, project_id: str | None = None) -> list[dict[str, Any]]:
    conn = _connect()
    try:
        if project_id is None:
            rows = conn.execute(
                "SELECT source_id, project_id, source_type, title, hindsight_document_id, created_at FROM sources ORDER BY created_at, source_id"
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT source_id, project_id, source_type, title, hindsight_document_id, created_at FROM sources WHERE project_id = ? ORDER BY created_at, source_id",
                (project_id,),
            ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def list_decision_records(*, project_id: str | None = None) -> list[dict[str, Any]]:
    conn = _connect()
    try:
        if project_id is None:
            rows = conn.execute(
                "SELECT decision_id, project_id, title, decision_statement, occurred_at, status, superseded_by, created_at, updated_at FROM decisions ORDER BY occurred_at, decision_id"
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT decision_id, project_id, title, decision_statement, occurred_at, status, superseded_by, created_at, updated_at FROM decisions WHERE project_id = ? ORDER BY occurred_at, decision_id",
                (project_id,),
            ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def list_outcome_records(*, decision_id: str | None = None) -> list[dict[str, Any]]:
    conn = _connect()
    try:
        if decision_id is None:
            rows = conn.execute(
                "SELECT outcome_id, project_id, decision_id, title, summary, created_at FROM outcomes ORDER BY created_at, outcome_id"
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT outcome_id, project_id, decision_id, title, summary, created_at FROM outcomes WHERE decision_id = ? ORDER BY created_at, outcome_id",
                (decision_id,),
            ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def list_causal_link_records(*, decision_id: str) -> list[dict[str, Any]]:
    conn = _connect()
    try:
        rows = conn.execute(
            "SELECT causal_link_id, decision_id, outcome_id, relation, evidence_ids, created_at FROM causal_links WHERE decision_id = ? ORDER BY created_at, causal_link_id",
            (decision_id,),
        ).fetchall()
        result = [dict(row) for row in rows]
        for item in result:
            item["evidence_ids"] = _deserialize_json(item["evidence_ids"]) or []
        return result
    finally:
        conn.close()


def get_record_counts() -> dict[str, int]:
    conn = _connect()
    try:
        tables = ("projects", "sources", "decisions", "audit_events")
        return {
            table: int(conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])
            for table in tables
        }
    finally:
        conn.close()


def save_source(
    source_id: str,
    project_id: str,
    *,
    source_type: str | None = None,
    hindsight_document_id: str | None = None,
    title: str | None = None,
) -> dict[str, Any]:
    conn = _connect()
    try:
        conn.execute(
            """
            INSERT INTO sources(source_id, project_id, source_type, hindsight_document_id, title)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(source_id)
            DO UPDATE SET project_id = excluded.project_id,
                          source_type = excluded.source_type,
                          hindsight_document_id = excluded.hindsight_document_id,
                          title = excluded.title
            """,
            (source_id, project_id, source_type, hindsight_document_id, title),
        )
        conn.commit()
        return get_source(source_id)
    finally:
        conn.close()


def get_source(source_id: str) -> dict[str, Any]:
    conn = _connect()
    try:
        row = conn.execute(
            "SELECT source_id, project_id, source_type, hindsight_document_id, title, created_at FROM sources WHERE source_id = ?",
            (source_id,),
        ).fetchone()
        if row is None:
            raise KeyError(source_id)
        return dict(row)
    finally:
        conn.close()


def save_decision(
    decision_id: str,
    project_id: str,
    *,
    title: str | None = None,
    decision_statement: str | None = None,
    occurred_at: str | None = None,
    status: str = "active",
    superseded_by: str | None = None,
) -> dict[str, Any]:
    conn = _connect()
    try:
        now = _now_utc()
        conn.execute(
            """
            INSERT INTO decisions(
                decision_id,
                project_id,
                title,
                decision_statement,
                occurred_at,
                status,
                superseded_by,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(decision_id)
            DO UPDATE SET project_id = excluded.project_id,
                          title = excluded.title,
                          decision_statement = excluded.decision_statement,
                          occurred_at = excluded.occurred_at,
                          status = excluded.status,
                          superseded_by = excluded.superseded_by,
                          updated_at = excluded.updated_at
            """,
            (decision_id, project_id, title, decision_statement, occurred_at, status, superseded_by, now, now),
        )
        conn.commit()
        return get_decision_record(decision_id)
    finally:
        conn.close()


def get_decision_record(decision_id: str) -> dict[str, Any]:
    conn = _connect()
    try:
        row = conn.execute(
            "SELECT decision_id, project_id, title, decision_statement, occurred_at, status, superseded_by, created_at, updated_at FROM decisions WHERE decision_id = ?",
            (decision_id,),
        ).fetchone()
        if row is None:
            raise KeyError(decision_id)
        return dict(row)
    finally:
        conn.close()


def mark_decision_status(decision_id: str, status: str, *, superseded_by: str | None = None) -> dict[str, Any]:
    conn = _connect()
    try:
        conn.execute(
            "UPDATE decisions SET status = ?, superseded_by = ?, updated_at = ? WHERE decision_id = ?",
            (status, superseded_by, _now_utc(), decision_id),
        )
        conn.commit()
        return get_decision_record(decision_id)
    finally:
        conn.close()


def save_project_context(
    project_id: str,
    *,
    consumer_count: int | None = None,
    replay_required: bool | None = None,
    current_project: str | None = None,
    context_json: dict[str, Any] | None = None,
) -> dict[str, Any]:
    conn = _connect()
    try:
        payload = context_json or {}
        conn.execute(
            """
            INSERT INTO project_context(
                project_id,
                consumer_count,
                replay_required,
                current_project,
                context_json,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(project_id)
            DO UPDATE SET consumer_count = excluded.consumer_count,
                          replay_required = excluded.replay_required,
                          current_project = excluded.current_project,
                          context_json = excluded.context_json,
                          updated_at = excluded.updated_at
            """,
            (
                project_id,
                consumer_count,
                1 if replay_required is True else 0 if replay_required is False else None,
                current_project,
                _serialize_json(payload),
                _now_utc(),
            ),
        )
        conn.commit()
        return get_project_context_record(project_id)
    finally:
        conn.close()


def get_project_context_record(project_id: str) -> dict[str, Any]:
    conn = _connect()
    try:
        row = conn.execute(
            "SELECT project_id, consumer_count, replay_required, current_project, context_json, updated_at FROM project_context WHERE project_id = ?",
            (project_id,),
        ).fetchone()
        if row is None:
            raise KeyError(project_id)
        payload = dict(row)
        payload["replay_required"] = bool(payload["replay_required"]) if payload["replay_required"] is not None else None
        payload["context_json"] = _deserialize_json(payload["context_json"])
        return payload
    finally:
        conn.close()


def save_outcome(
    outcome_id: str,
    project_id: str,
    *,
    decision_id: str | None = None,
    title: str | None = None,
    summary: str | None = None,
) -> dict[str, Any]:
    conn = _connect()
    try:
        conn.execute(
            """
            INSERT INTO outcomes(outcome_id, project_id, decision_id, title, summary)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(outcome_id)
            DO UPDATE SET project_id = excluded.project_id,
                          decision_id = excluded.decision_id,
                          title = excluded.title,
                          summary = excluded.summary
            """,
            (outcome_id, project_id, decision_id, title, summary),
        )
        conn.commit()
        return {
            "outcome_id": outcome_id,
            "project_id": project_id,
            "decision_id": decision_id,
            "title": title,
            "summary": summary,
        }
    finally:
        conn.close()


def save_causal_link(
    causal_link_id: str,
    *,
    decision_id: str,
    outcome_id: str | None = None,
    relation: str | None = None,
    evidence_ids: list[str] | None = None,
) -> dict[str, Any]:
    conn = _connect()
    try:
        conn.execute(
            """
            INSERT INTO causal_links(causal_link_id, decision_id, outcome_id, relation, evidence_ids)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(causal_link_id)
            DO UPDATE SET decision_id = excluded.decision_id,
                          outcome_id = excluded.outcome_id,
                          relation = excluded.relation,
                          evidence_ids = excluded.evidence_ids
            """,
            (causal_link_id, decision_id, outcome_id, relation, _serialize_json(evidence_ids or [])),
        )
        conn.commit()
        return {
            "causal_link_id": causal_link_id,
            "decision_id": decision_id,
            "outcome_id": outcome_id,
            "relation": relation,
            "evidence_ids": evidence_ids or [],
        }
    finally:
        conn.close()


def record_audit_event(
    *,
    action: str,
    role: str,
    project_id: str | None = None,
    query_id: str | None = None,
    decision_ids: list[str] | None = None,
    output_hash: str | None = None,
    recalled_memory_ids: list[str] | None = None,
    scope: Scope | None = None,
    actor: str | None = None,
) -> dict[str, Any]:
    conn = _connect()
    try:
        conn.execute(
            """
            INSERT INTO audit_events(
                action,
                role,
                project_id,
                query_id,
                decision_ids,
                output_hash,
                recalled_memory_ids,
                scope_json,
                actor
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                action,
                role,
                project_id,
                query_id,
                _serialize_json(decision_ids or []),
                output_hash,
                _serialize_json(recalled_memory_ids or []),
                _serialize_json(
                    {
                        "allowed_projects": getattr(scope, "allowed_projects", None),
                        "allowed_tags": getattr(scope, "allowed_tags", None),
                        "visibility": getattr(scope, "visibility", None),
                    }
                )
                if scope is not None
                else None,
                actor,
            ),
        )
        conn.commit()
        last_row_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        row = conn.execute(
            "SELECT event_id, timestamp, action, role, project_id, query_id, decision_ids, output_hash, recalled_memory_ids, scope_json, actor FROM audit_events WHERE event_id = ?",
            (last_row_id,),
        ).fetchone()
        return dict(row)
    finally:
        conn.close()


def list_audit_events(*, project_id: str | None = None, role: str | None = None) -> list[dict[str, Any]]:
    conn = _connect()
    try:
        query = "SELECT event_id, timestamp, action, role, project_id, query_id, decision_ids, output_hash, recalled_memory_ids, scope_json, actor FROM audit_events"
        clauses: list[str] = []
        params: list[Any] = []
        if project_id is not None:
            clauses.append("project_id = ?")
            params.append(project_id)
        if role is not None:
            clauses.append("role = ?")
            params.append(role)
        if clauses:
            query += " WHERE " + " AND ".join(clauses)
        query += " ORDER BY timestamp DESC, event_id DESC"
        rows = conn.execute(query, params).fetchall()
        results: list[dict[str, Any]] = []
        for row in rows:
            payload = dict(row)
            payload["decision_ids"] = _deserialize_json(payload["decision_ids"]) or []
            payload["recalled_memory_ids"] = _deserialize_json(payload["recalled_memory_ids"]) or []
            payload["scope_json"] = _deserialize_json(payload["scope_json"])
            results.append(payload)
        return results
    finally:
        conn.close()


def resolve_scope(role: str) -> Scope:
    role = (role or "viewer").lower()
    if role in {"admin", "executive", "project_lead"}:
        return Scope(
            role=role,
            allowed_tags=["decision", "technology", "risk", "decisionprint"],
            visibility="organization",
        )
    if role == "lead":
        return Scope(
            role="lead",
            allowed_projects=["project-001", "project-002"],
            allowed_tags=["decision", "technology", "risk", "decisionprint"],
            visibility="project",
        )
    if role == "engineer":
        return Scope(
            role="engineer",
            allowed_projects=[],
            allowed_tags=["decision", "technology"],
            visibility="project",
        )
    if role == "reviewer":
        return Scope(
            role="reviewer",
            allowed_projects=["project-001", "project-002"],
            allowed_tags=["risk", "decisionprint"],
            visibility="project",
        )
    return Scope(
        role="viewer",
        allowed_projects=["project-001"],
        allowed_tags=["decisionprint"],
        visibility="project",
    )


def assert_project_allowed(scope: Scope, project_id: str) -> None:
    if scope.role == "engineer" and project_id.lower() == "delta":
        raise ScopeError(f"Project '{project_id}' is not allowed for role '{scope.role}'")
    if scope.allowed_projects and project_id not in scope.allowed_projects:
        raise ScopeError(f"Project '{project_id}' is not allowed for role '{scope.role}'")


__all__ = [
    "ScopeError",
    "Scope",
    "init_database",
    "upsert_project",
    "get_project",
    "list_projects_in_scope",
    "list_project_records",
    "list_source_records",
    "list_decision_records",
    "list_outcome_records",
    "list_causal_link_records",
    "get_record_counts",
    "save_source",
    "get_source",
    "save_decision",
    "get_decision_record",
    "mark_decision_status",
    "save_project_context",
    "get_project_context_record",
    "save_outcome",
    "save_causal_link",
    "record_audit_event",
    "list_audit_events",
    "resolve_scope",
    "assert_project_allowed",
]
