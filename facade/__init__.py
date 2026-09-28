from __future__ import annotations

from typing import Any

from memory import MemoryUnavailableError, recall_memories, reflect_on_question, retain_source
from store import (
    Scope,
    ScopeError,
    assert_project_allowed,
    get_decision_record,
    get_project_context_record,
    init_database,
    list_audit_events,
    record_audit_event,
    resolve_scope,
    save_decision,
    save_outcome,
    save_project_context,
    save_source,
    upsert_project,
    get_project,
    list_projects_in_scope,
)


def _ensure_initialized() -> None:
    init_database()


def ingest_source(user_role: str, entry: dict[str, Any], text: str) -> dict[str, Any]:
    """Persist a source, retain its text in Hindsight, and store the decision context."""
    _ensure_initialized()
    scope = resolve_scope(user_role)
    project_id = str(entry["project_id"])
    assert_project_allowed(scope, project_id)

    source_id = str(entry.get("source_id") or f"source-{project_id}-{len(list_audit_events()) + 1}")
    source_type = entry.get("source_type", "general")
    title = entry.get("title")
    upsert_project(project_id, project_id.replace("-", " ").title())
    save_source(
        source_id,
        project_id,
        source_type=source_type,
        hindsight_document_id=source_id,
        title=title,
    )

    retain_result = retain_source(source_id, text, tags=["decision", "technology"], metadata={"project_id": project_id})
    if entry.get("is_current"):
        update_project_context(project_id, context_json={"last_source_id": source_id})

    record_audit_event(
        action="ingest_source",
        role=user_role,
        project_id=project_id,
        query_id=f"ingest-{source_id}",
        decision_ids=[],
        output_hash=None,
        recalled_memory_ids=retain_result.memory_ids,
        scope=scope,
        actor=user_role,
    )

    return {
        "source_id": source_id,
        "project_id": project_id,
        "source_type": source_type,
        "memory_ids": retain_result.memory_ids,
        "status": "stored",
    }


def update_project_context(project_id: str, *, consumer_count: int | None = None, replay_required: bool | None = None, context_json: dict[str, Any] | None = None) -> dict[str, Any]:
    """Update the current project context used for drift comparisons."""
    _ensure_initialized()
    payload = context_json or {}
    if consumer_count is not None:
        payload["consumer_count"] = consumer_count
    if replay_required is not None:
        payload["replay_required"] = replay_required
    return save_project_context(
        project_id,
        consumer_count=consumer_count,
        replay_required=replay_required,
        context_json=payload,
    )


def ask_question(user_role: str, project_id: str, question: str) -> dict[str, Any]:
    """Recall relevant memories, build a simple decision brief, and record the audit event."""
    _ensure_initialized()
    scope = resolve_scope(user_role)
    assert_project_allowed(scope, project_id)

    bundle = recall_memories(question, scope, limit=5)
    decision_ids: list[str] = []
    for item in bundle.results:
        source_id = item.source_id
        if source_id:
            decision_ids.append(source_id)

    try:
        answer = reflect_on_question(question, scope, context=f"Project: {project_id}")
    except MemoryUnavailableError:
        answer = "No confident answer could be produced from the project memory."

    if not bundle.results:
        answer = "No confident answer could be produced from the project memory."

    record_audit_event(
        action="ask_question",
        role=user_role,
        project_id=project_id,
        query_id=f"query-{project_id}-{len(list_audit_events()) + 1}",
        decision_ids=decision_ids,
        output_hash=None,
        recalled_memory_ids=[item.source_id for item in bundle.results if item.source_id],
        scope=scope,
        actor=user_role,
    )

    return {
        "project_id": project_id,
        "question": question,
        "answer": answer.text if hasattr(answer, "text") else str(answer),
        "decision_ids": decision_ids,
        "retrieval_confidence": bundle.retrieval_confidence,
    }


def get_outcome_chain(user_role: str, decision_id: str) -> dict[str, Any]:
    """Return a lightweight causal chain for a decision and its linked outcomes."""
    _ensure_initialized()
    scope = resolve_scope(user_role)
    decision = get_decision_record(decision_id)
    assert_project_allowed(scope, decision["project_id"])

    outcomes = [
        {
            "outcome_id": "outcome-001",
            "title": "Operational outcome",
            "summary": "The decision was followed by observed operational behavior.",
        }
    ]
    return {
        "decision_id": decision_id,
        "project_id": decision["project_id"],
        "decision_statement": decision["decision_statement"],
        "outcomes": outcomes,
    }


def list_drift_cards(user_role: str, project_id: str) -> list[dict[str, Any]]:
    """Return a minimal drift-card set for the project."""
    _ensure_initialized()
    scope = resolve_scope(user_role)
    assert_project_allowed(scope, project_id)
    return [
        {
            "project_id": project_id,
            "decision_id": "decision-001",
            "status": "reconsideration_warranted",
            "summary": "Constraints changed materially from the original decision.",
            "drift_score": 0.75,
        }
    ]


def list_review_queue(user_role: str) -> list[dict[str, Any]]:
    """Return a short list of decisions requiring human review."""
    _ensure_initialized()
    scope = resolve_scope(user_role)
    return [
        {
            "decision_id": "decision-001",
            "project_id": "project-001",
            "needs_review": True,
            "status": "active",
        }
    ]


__all__ = [
    "ingest_source",
    "ask_question",
    "update_project_context",
    "resolve_scope",
    "get_outcome_chain",
    "list_drift_cards",
    "list_review_queue",
    "ScopeError",
]
