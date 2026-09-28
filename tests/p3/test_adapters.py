"""Tests for backend adapters and FacadeProtocol conformance."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from contracts import DecisionFilter, SourceManifestEntry, SourceType
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


def test_live_backend_lazy_import() -> None:
    """LiveBackend must not crash on import or module definition; handles missing facade at runtime."""
    # Instantiating LiveBackend without facade should raise MemoryUnavailableError
    from contracts.errors import MemoryUnavailableError

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
