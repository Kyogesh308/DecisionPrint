from __future__ import annotations

import sqlite3

import pytest

from store import (
    Scope,
    ScopeError,
    assert_project_allowed,
    get_decision_record,
    get_project,
    get_project_context_record,
    get_source,
    init_database,
    list_audit_events,
    list_projects_in_scope,
    mark_decision_status,
    record_audit_event,
    resolve_scope,
    save_decision,
    save_outcome,
    save_project_context,
    save_source,
    save_causal_link,
    upsert_project,
)


def test_database_round_trip_and_audit(tmp_path):
    db_path = tmp_path / "decisionprint.db"
    init_database(str(db_path))

    upsert_project("project-001", "Alpha", description="Kafka discussion")
    save_source(
        "source-001",
        "project-001",
        source_type="architecture_doc",
        hindsight_document_id="doc-123",
        title="Kafka constraints",
    )
    save_decision(
        "decision-001",
        "project-001",
        title="Kafka rejection",
        decision_statement="Kafka was rejected because the project had two consumers and no replay requirement.",
        occurred_at="2025-01-15T09:30:00Z",
        status="active",
    )
    save_project_context(
        "project-001",
        consumer_count=2,
        replay_required=False,
        current_project="alpha",
    )
    save_outcome(
        "outcome-001",
        "project-001",
        decision_id="decision-001",
        title="Postmortem",
        summary="No replay outage", 
    )
    save_causal_link(
        "link-001",
        decision_id="decision-001",
        outcome_id="outcome-001",
        relation="explains",
        evidence_ids=["evidence-1"],
    )
    record_audit_event(
        action="ask_question",
        role="lead",
        project_id="project-001",
        query_id="q-001",
        decision_ids=["decision-001"],
        output_hash="abc123",
    )

    project = get_project("project-001")
    assert project["project_id"] == "project-001"
    assert project["name"] == "Alpha"

    source = get_source("source-001")
    assert source["source_type"] == "architecture_doc"

    decision = get_decision_record("decision-001")
    assert decision["decision_statement"].startswith("Kafka was rejected")

    context = get_project_context_record("project-001")
    assert context["consumer_count"] == 2

    assert list_audit_events(project_id="project-001")[0]["action"] == "ask_question"

    mark_decision_status("decision-001", "superseded", superseded_by="decision-002")
    updated = get_decision_record("decision-001")
    assert updated["status"] == "superseded"
    assert updated["superseded_by"] == "decision-002"

    connection = sqlite3.connect(str(db_path))
    tables = connection.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    ).fetchall()
    assert {row[0] for row in tables} >= {
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


def test_resolve_scope_and_project_access_rules():
    init_database()
    upsert_project("project-001", "Alpha")
    upsert_project("project-002", "Beta")

    scope = resolve_scope("lead")
    assert isinstance(scope, Scope)
    assert scope.role == "lead"
    assert scope.allowed_projects
    assert "decisionprint" in scope.allowed_tags or scope.allowed_tags

    assert_project_allowed(scope, scope.allowed_projects[0])

    with pytest.raises(ScopeError):
        assert_project_allowed(scope, "blocked-project")

    public_scope = resolve_scope("viewer")
    assert public_scope.role == "viewer"
    assert public_scope.allowed_tags
    assert list_projects_in_scope(public_scope)


def test_init_database_is_idempotent(tmp_path):
    db_path = tmp_path / "decisionprint.db"
    init_database(str(db_path))
    init_database(str(db_path))
    assert db_path.exists()
