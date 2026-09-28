"""Tests for backend adapters and FacadeProtocol conformance."""

from __future__ import annotations

import builtins
from datetime import UTC, datetime

import pytest

from contracts import Constraint, CurrentProjectContext, DecisionFilter, SourceManifestEntry, SourceType
from contracts.errors import ScopeError
from contracts.interfaces import FacadeProtocol
from ui.adapters import get_backend
from ui.adapters.fixture_backend import FixtureBackend
from ui.adapters.live_backend import LiveBackend


def test_fixture_backend_protocol_conformance() -> None:
    """FixtureBackend must implement all 16 methods of FacadeProtocol."""
    fb = FixtureBackend()
    assert isinstance(fb, FacadeProtocol)


def test_get_backend_reads_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """get_backend must return FixtureBackend when DP_BACKEND=fixture."""
    monkeypatch.setenv("DP_BACKEND", "fixture")
    backend = get_backend()
    assert isinstance(backend, FixtureBackend)

    monkeypatch.setenv("DP_BACKEND", "invalid_mode")
    with pytest.raises(ValueError, match="Unknown DP_BACKEND"):
        get_backend()


def test_live_backend_connects_ui_calls_to_sqlite_and_hindsight(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    from types import SimpleNamespace

    import memory

    class FakeHindsight:
        def __init__(self, base_url: str, api_key: str | None = None):
            assert base_url == "https://memory.example"
            assert api_key == "test-key"

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            return False

        def retain(self, **kwargs):
            return SimpleNamespace(operation_ids=["op-1"])

        def recall(self, **kwargs):
            return SimpleNamespace(
                results=[
                    SimpleNamespace(
                        id="memory-1",
                        text="Kafka was rejected because the project had two consumers.",
                        document_id="SRC-NOVA-901",
                        metadata={"source_id": "SRC-NOVA-901"},
                        tags=["decision"],
                        scores=SimpleNamespace(final=0.9),
                    )
                ]
            )

        def reflect(self, **kwargs):
            return SimpleNamespace(text="The previous Kafka decision depended on different constraints.")

        def list_mental_models(self, **kwargs):
            return SimpleNamespace(items=[])

    monkeypatch.setenv("DP_BACKEND", "live")
    monkeypatch.setenv("DP_DB_PATH", str(tmp_path / "decisionprint.db"))
    monkeypatch.setenv("DP_HINDSIGHT_BASE_URL", "https://memory.example")
    monkeypatch.setenv("DP_HINDSIGHT_API_KEY", "test-key")
    monkeypatch.setenv("DP_HINDSIGHT_BANK_ID", "test-bank")
    monkeypatch.setattr(memory, "Hindsight", FakeHindsight)

    backend = get_backend()
    assert isinstance(backend, LiveBackend)

    entry = SourceManifestEntry(
        source_id="SRC-NOVA-901",
        project_id="nova",
        source_type=SourceType.adr,
        title="Kafka decision",
        date=datetime.now(tz=UTC),
        is_current=True,
    )
    ingested = backend.ingest_source(entry, "Kafka was rejected because there were two consumers.", "admin")
    overview = backend.get_memory_overview("admin")
    projects = backend.list_projects("admin")
    updated_context = backend.update_project_context(
        CurrentProjectContext(project_id="nova", constraints=[Constraint(key="consumer_count", value=15)]), "admin"
    )
    from store import save_causal_link, save_decision, save_outcome

    save_decision(
        "DEC-NOVA-901",
        "nova",
        title="Kafka selection",
        decision_statement="Kafka was reconsidered for Nova.",
        occurred_at="2026-02-01T00:00:00Z",
    )
    save_outcome("OUT-NOVA-901", "nova", decision_id="DEC-NOVA-901", title="Review", summary="Review completed")
    save_causal_link(
        "LINK-NOVA-901",
        decision_id="DEC-NOVA-901",
        outcome_id="OUT-NOVA-901",
        relation="explicit_causal_link",
        evidence_ids=[entry.source_id],
    )
    decisions = backend.search_decisions(DecisionFilter(text="Kafka"), "admin")
    decision = backend.get_decision("DEC-NOVA-901", "admin")
    timeline = backend.get_decision_timeline("DEC-NOVA-901", "admin")
    brief = backend.ask_question("Should Nova use Kafka?", "nova", "admin")
    trace = backend.get_memory_trace(brief.query_id, "admin")
    evidence = backend.get_evidence(entry.source_id, "admin")
    outcome_chain = backend.get_outcome_chain("DEC-NOVA-901", "admin")
    drift_cards = backend.list_drift_cards("nova", "admin")
    observations = backend.list_observations("admin")
    mental_models = backend.list_mental_models("admin")
    review_queue = backend.list_review_queue("admin")

    assert ingested.source_id == entry.source_id
    assert ingested.memories_created == 1
    assert overview.source_count == 1
    assert projects[0].project_id == "nova"
    assert updated_context.constraints["consumer_count"] == "15"
    assert decisions[0].decision_id == "DEC-NOVA-901"
    assert decision.title == "Kafka selection"
    assert len(timeline) == 2
    assert brief.answer_summary.startswith("The previous Kafka decision")
    assert brief.source_ids == [entry.source_id]
    assert trace.recalled[0].memory_id == "memory-1"
    assert evidence.source_id == entry.source_id
    assert outcome_chain.links[0].evidence_ids == [entry.source_id]
    assert drift_cards == []
    assert observations == mental_models == review_queue == []


def test_live_backend_lazy_import(monkeypatch: pytest.MonkeyPatch) -> None:
    """LiveBackend reports a missing facade at construction time."""
    from contracts.errors import MemoryUnavailableError

    original_import = builtins.__import__

    def import_without_facade(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "facade":
            raise ImportError("Facade module not available")
        return original_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", import_without_facade)
    with pytest.raises(MemoryUnavailableError, match="Facade module not available"):
        LiveBackend()


def test_fixture_backend_all_16_methods_callable() -> None:
    """Call every one of the 16 FacadeProtocol methods with realistic arguments."""
    fb = FixtureBackend()
    role = "admin"

    # 1. get_memory_overview
    ov = fb.get_memory_overview(role)
    assert ov.project_count >= 1

    # 2. list_projects
    projs = fb.list_projects(role)
    assert len(projs) >= 2

    # 3. get_project_context
    ctx = fb.get_project_context("nova", role)
    assert ctx.project_name == "Project Nova"

    # 4. update_project_context
    ctx.constraints["test_key"] = "test_val"
    updated = fb.update_project_context(ctx, role)
    assert updated.constraints["test_key"] == "test_val"

    # 5. ingest_source
    entry = SourceManifestEntry(
        source_id="SRC-NOVA-999",
        project_id="nova",
        source_type=SourceType.meeting_transcript,
        title="Test Ingest",
        file_path="current/nova/SRC-NOVA-999.md",
        date=datetime.now(tz=UTC),
        is_current=True,
    )
    initial_facts = fb.get_memory_overview(role).fact_count
    res = fb.ingest_source(entry, "# Meeting Notes\nSome facts were discussed.", role)
    assert res.memories_created > 0
    assert fb.get_memory_overview(role).fact_count > initial_facts

    # 6. search_decisions
    decs = fb.search_decisions(DecisionFilter(text="Kafka"), role)
    assert len(decs) >= 1
    assert decs[0].decision_id == "DEC-ALPHA-001"

    # 7. get_decision
    dec = fb.get_decision("DEC-ALPHA-001", role)
    assert dec.selected_option == "RabbitMQ"

    # 8. get_decision_timeline
    tl = fb.get_decision_timeline("DEC-ALPHA-001", role)
    assert len(tl) >= 2

    # 9. ask_question
    brief = fb.ask_question("Should Nova use Kafka?", "nova", role)
    assert brief.drift is not None

    # 10. list_drift_cards
    cards = fb.list_drift_cards("nova", role)
    assert len(cards) >= 1

    # 11. get_evidence
    ev = fb.get_evidence("SRC-ALPHA-001", role)
    assert ev.source_id == "SRC-ALPHA-001"

    # 12. get_outcome_chain
    chain = fb.get_outcome_chain("DEC-DELTA-001", role)
    assert chain.decision_id == "DEC-DELTA-001"

    # 13. list_observations
    obs = fb.list_observations(role)
    assert len(obs) >= 1

    # 14. list_mental_models
    models = fb.list_mental_models(role)
    assert len(models) >= 1

    # 15. get_memory_trace
    trace = fb.get_memory_trace("q-nova-kafka-001", role)
    assert trace.query_id == "q-nova-kafka-001"

    # 16. list_review_queue
    rq = fb.list_review_queue(role)
    assert len(rq) >= 1


def test_fixture_backend_scope_error_enforcement() -> None:
    """Engineer role accessing confidential Delta project must raise ScopeError."""
    fb = FixtureBackend()

    # Engineer cannot view Delta
    with pytest.raises(ScopeError, match="confidential"):
        fb.get_project_context("delta", "engineer")

    with pytest.raises(ScopeError, match="Access denied"):
        fb.get_evidence("SRC-DELTA-001", "engineer")

    # Admin and Executive CAN view Delta
    ctx = fb.get_project_context("delta", "admin")
    assert "delta" in ctx.project_id
    ctx_exec = fb.get_project_context("delta", "executive")
    assert "delta" in ctx_exec.project_id


def test_ask_question_suggestion_chips_routing() -> None:
    """Every Ask suggestion chip must return a valid brief on FixtureBackend."""
    fb = FixtureBackend()
    role = "admin"

    chip_queries = [
        ("Should Nova use Kafka?", "nova"),
        ("Why was GraphQL rejected?", "nova"),
        ("What happened after Cedar skipped backups?", "delta"),
        ("Has our Redis position changed?", "nova"),
    ]
    for q, proj in chip_queries:
        brief = fb.ask_question(q, proj, role)
        assert brief is not None
        assert brief.project_id == proj
