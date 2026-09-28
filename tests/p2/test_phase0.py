"""
tests/p2/test_phase0.py

Phase 0 smoke tests: fixtures load correctly, LLM wrapper stubs are importable,
contracts models validate, and the module public API matches __all__.
"""

import pytest

from contracts.models import CurrentProjectContext, Decision, RecallBundle

# ── Fixture loading ──────────────────────────────────────────────────────────


class TestFixtureLoading:
    def test_decision_alpha_kafka_loads(self):
        from tests.p2.fixtures.loader import load_decision_alpha_kafka

        d = load_decision_alpha_kafka()
        assert isinstance(d, Decision)
        assert d.id == "DEC-ALPHA-001"
        assert d.project_id == "alpha"
        assert d.status == "active"

    def test_decision_has_four_reason_linked_constraints(self):
        from tests.p2.fixtures.loader import load_decision_alpha_kafka

        d = load_decision_alpha_kafka()
        reason_linked = [c for c in d.constraints if c.is_reason_linked]
        assert len(reason_linked) == 4

    def test_decision_constraint_consumer_count_is_two(self):
        from tests.p2.fixtures.loader import load_decision_alpha_kafka

        d = load_decision_alpha_kafka()
        cc = next(c for c in d.constraints if c.key == "consumer_count")
        assert cc.value == 2
        assert cc.is_reason_linked is True

    def test_context_nova_loads(self):
        from tests.p2.fixtures.loader import load_context_nova

        ctx = load_context_nova()
        assert isinstance(ctx, CurrentProjectContext)
        assert ctx.project_id == "nova"
        cc = next(c for c in ctx.constraints if c.key == "consumer_count")
        assert cc.value == 15

    def test_recall_bundle_kafka_loads(self):
        from tests.p2.fixtures.loader import load_recall_bundle_kafka

        rb = load_recall_bundle_kafka()
        assert isinstance(rb, RecallBundle)
        assert len(rb.memories) == 3
        assert "DEC-ALPHA-001" in rb.decision_ids
        assert rb.retrieval_confidence > 0.8

    def test_recall_bundle_cedar_loads(self):
        from tests.p2.fixtures.loader import load_recall_bundle_cedar

        rb = load_recall_bundle_cedar()
        assert isinstance(rb, RecallBundle)
        assert len(rb.memories) == 2
        postmortem = rb.memories[0]
        assert "backup" in postmortem.text.lower()


# ── Public API surface ───────────────────────────────────────────────────────


class TestPublicAPI:
    def test_intelligence_all_exports_present(self):
        import intelligence

        expected = {
            "extract_decisions",
            "extract_outcomes",
            "extract_current_context",
            "normalize_constraints",
            "compare_constraints",
            "score_drift",
            "classify_causal_link",
            "build_decision_brief",
        }
        assert set(intelligence.__all__) == expected

    def test_intelligence_functions_importable(self):
        # All must be callable (even if they raise NotImplementedError)

        from intelligence import (
            build_decision_brief,
            classify_causal_link,
            compare_constraints,
            extract_current_context,
            extract_decisions,
            extract_outcomes,
            normalize_constraints,
            score_drift,
        )

        for fn in [
            normalize_constraints,
            compare_constraints,
            score_drift,
            build_decision_brief,
            extract_decisions,
            extract_outcomes,
            extract_current_context,
            classify_causal_link,
        ]:
            assert callable(fn)


# ── Config ───────────────────────────────────────────────────────────────────


class TestConfig:
    def test_get_settings_returns_settings_object(self, monkeypatch):
        monkeypatch.setenv("DP_LLM_API_KEY", "sk-test")
        monkeypatch.setenv("DP_LLM_PROVIDER", "anthropic")
        # Clear the LRU cache so monkeypatching takes effect
        from intelligence.config import get_settings

        get_settings.cache_clear()
        s = get_settings()
        assert s.llm_provider == "anthropic"
        assert s.llm_api_key == "sk-test"
        get_settings.cache_clear()

    def test_get_settings_allows_cache_use_when_api_key_missing(self, monkeypatch):
        monkeypatch.setenv("DP_LLM_API_KEY", "")
        from intelligence.config import get_settings

        get_settings.cache_clear()
        assert get_settings().llm_api_key == ""
        get_settings.cache_clear()
