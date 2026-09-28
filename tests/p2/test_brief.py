"""
tests/p2/test_brief.py
"""

import json

import pytest

from contracts.enums import DriftLevel, EpistemicLabel, Role
from contracts.errors import MemoryUnavailableError
from contracts.models import BriefClaim, DecisionBrief, ReflectResult, Scope, SourceRef
from intelligence import build_decision_brief
from tests.p2.fixtures.loader import (
    build_fixture_brief_nova_kafka,
    load_context_nova,
    load_decision_alpha_kafka,
    load_recall_bundle_kafka,
)


def _make_scope() -> Scope:
    return Scope(
        role=Role.ENGINEER,
        allowed_project_ids=["alpha", "nova"],
        allowed_tags=[],
        visibility_levels=["internal"],
    )


def _fixed_reflect_fn(synthesis_json: str):
    def _fn(
        question: str, scope: Scope, *, context: str | None = None
    ) -> ReflectResult:
        return ReflectResult(
            text=synthesis_json,
            memory_ids=["mem-alpha-001", "mem-alpha-002", "mem-nova-001"],
            source_refs=[
                SourceRef(source_id="SRC-ALPHA-001"),
                SourceRef(source_id="SRC-NOVA-001"),
            ],
        )

    return _fn


def _minimal_synthesis_json(*, reconsideration: bool = True) -> str:
    closing = (
        "Reconsideration warranted." if reconsideration else "Original decision holds."
    )
    return json.dumps(
        {
            "answer_summary": "Test answer summary.",
            "historical_decisions": [
                {
                    "text": "Alpha rejected Kafka due to low consumer count.",
                    "label": "FACT",
                    "memory_ids": ["mem-alpha-001"],
                    "source_refs": [{"source_id": "SRC-ALPHA-001"}],
                }
            ],
            "observations": [
                {
                    "text": "Nova now has 15 consumers — fundamentally different from Alpha's two.",
                    "label": "OBSERVATION",
                    "memory_ids": ["mem-nova-001"],
                    "source_refs": [],
                }
            ],
            "inferences": [
                {
                    "text": "The replay requirement reversal is the most significant driver of drift.",
                    "label": "INFERENCE",
                    "memory_ids": ["mem-alpha-002", "mem-nova-001"],
                    "source_refs": [],
                }
            ],
            "recommendation": {
                "text": f"Three foundational premises have changed. {closing}",
                "label": "RECOMMENDATION",
                "memory_ids": ["mem-alpha-001"],
                "source_refs": [],
            },
        }
    )


class TestFixtureBriefNovaKafka:
    @pytest.fixture(scope="class")
    def brief(self) -> DecisionBrief:
        return build_fixture_brief_nova_kafka()

    def test_brief_has_high_drift(self, brief: DecisionBrief):
        assert brief.drift is not None
        assert brief.drift.level == DriftLevel.HIGH, (
            f"Expected HIGH drift, got {brief.drift.level}"
        )

    def test_brief_reconsideration_warranted(self, brief: DecisionBrief):
        assert brief.reconsideration_warranted is True

    def test_brief_has_three_changed_reason_linked_premises(self, brief: DecisionBrief):
        from contracts.enums import ConstraintComparison

        changed_reason_linked = []
        for delta in brief.constraint_differences:
            for item in delta.items:
                if (
                    item.is_reason_linked
                    and item.comparison == ConstraintComparison.CHANGED
                ):
                    changed_reason_linked.append(item)
        assert len(changed_reason_linked) >= 3, (
            f"Expected ≥3 changed reason-linked constraints, got {len(changed_reason_linked)}: "
            f"{[i.key for i in changed_reason_linked]}"
        )

    def test_all_claims_are_cited(self, brief: DecisionBrief):
        all_claims: list[BriefClaim] = (
            brief.historical_decisions
            + brief.observations
            + brief.inferences
            + [brief.recommendation]
        )
        uncited = [c for c in all_claims if not c.source_refs and not c.memory_ids]
        non_rec_uncited = [
            c for c in uncited if c.label != EpistemicLabel.RECOMMENDATION
        ]
        assert not non_rec_uncited, (
            f"Found uncited non-recommendation claims: {[c.text[:60] for c in non_rec_uncited]}"
        )

    def test_recommendation_label_is_recommendation(self, brief: DecisionBrief):
        assert brief.recommendation.label == EpistemicLabel.RECOMMENDATION

    def test_recommendation_ends_with_warranted_or_holds(self, brief: DecisionBrief):
        text = brief.recommendation.text
        assert text.endswith("Reconsideration warranted.") or text.endswith(
            "Original decision holds."
        ), f"Recommendation does not end with a valid verdict: {text[-100:]!r}"

    def test_recommendation_never_says_use_kafka(self, brief: DecisionBrief):
        rec_text = brief.recommendation.text.lower()
        forbidden = [
            "use kafka",
            "adopt kafka",
            "choose kafka",
            "switch to kafka",
            "use redis",
            "adopt redis",
            "use rabbitmq",
        ]
        for phrase in forbidden:
            assert phrase not in rec_text, (
                f"Recommendation contains forbidden technology directive: {phrase!r}"
            )

    def test_brief_has_historical_decisions(self, brief: DecisionBrief):
        assert len(brief.historical_decisions) > 0

    def test_brief_has_observations(self, brief: DecisionBrief):
        assert len(brief.observations) > 0

    def test_brief_has_answer_summary(self, brief: DecisionBrief):
        assert brief.answer_summary and len(brief.answer_summary) > 20

    def test_brief_has_confidence_breakdown(self, brief: DecisionBrief):
        assert brief.confidence is not None
        assert brief.confidence.drift is not None
        assert 0.0 <= brief.confidence.drift <= 1.0

    def test_brief_sources_are_deduplicated(self, brief: DecisionBrief):
        source_ids = [s.source_id for s in brief.sources]
        assert len(source_ids) == len(set(source_ids)), (
            "Duplicate source IDs in brief.sources"
        )

    def test_brief_historical_constraints_populated(self, brief: DecisionBrief):
        assert len(brief.historical_constraints) > 0

    def test_brief_current_constraints_populated(self, brief: DecisionBrief):
        assert len(brief.current_constraints) > 0

    def test_brief_project_id_is_nova(self, brief: DecisionBrief):
        assert brief.project_id == "nova"

    def test_brief_generated_at_is_iso8601(self, brief: DecisionBrief):
        from datetime import datetime

        datetime.fromisoformat(brief.generated_at.replace("Z", "+00:00"))


class TestEpistemicLabels:
    def test_historical_decisions_are_facts(self):
        brief = build_fixture_brief_nova_kafka()
        for claim in brief.historical_decisions:
            assert claim.label == EpistemicLabel.FACT, (
                f"historical_decision claim has wrong label: {claim.label}"
            )

    def test_observations_are_observations(self):
        brief = build_fixture_brief_nova_kafka()
        for claim in brief.observations:
            assert claim.label == EpistemicLabel.OBSERVATION

    def test_inferences_are_inferences(self):
        brief = build_fixture_brief_nova_kafka()
        for claim in brief.inferences:
            assert claim.label == EpistemicLabel.INFERENCE


class TestReflectFnFallback:
    def test_brief_returns_when_reflect_fn_raises(self, monkeypatch):
        def failing_reflect_fn(question, scope, *, context=None):
            raise MemoryUnavailableError("Hindsight unavailable")

        decision = load_decision_alpha_kafka()
        context = load_context_nova()
        recall = load_recall_bundle_kafka()

        from intelligence import brief as brief_module

        monkeypatch.setattr(
            brief_module,
            "_fallback_reflect",
            lambda **kwargs: ReflectResult(
                text=_minimal_synthesis_json(),
                memory_ids=["mem-alpha-001"],
                source_refs=[SourceRef(source_id="SRC-ALPHA-001")],
            ),
        )

        result = build_decision_brief(
            query_id="test-fallback-001",
            query="Should Nova use Kafka?",
            scope=_make_scope(),
            recall=recall,
            decisions=[decision],
            current=context,
            reflect_fn=failing_reflect_fn,
        )

        assert isinstance(result, DecisionBrief)
        assert result.drift is not None
        assert result.recommendation is not None
        assert result.recommendation.label == EpistemicLabel.RECOMMENDATION

    def test_brief_returns_when_reflect_fn_and_fallback_both_fail(self, monkeypatch):
        def failing_reflect_fn(question, scope, *, context=None):
            raise MemoryUnavailableError("Hindsight unavailable")

        from intelligence import brief as brief_module

        monkeypatch.setattr(
            brief_module,
            "_fallback_reflect",
            lambda **kwargs: (_ for _ in ()).throw(
                LLMUnavailableError("LLM also down")
            ),
        )

        from contracts.errors import LLMUnavailableError

        def raising_fallback(**kwargs):
            raise LLMUnavailableError("LLM also down")

        monkeypatch.setattr(brief_module, "_fallback_reflect", raising_fallback)

        decision = load_decision_alpha_kafka()
        context = load_context_nova()
        recall = load_recall_bundle_kafka()

        result = build_decision_brief(
            query_id="test-double-fail-001",
            query="Should Nova use Kafka?",
            scope=_make_scope(),
            recall=recall,
            decisions=[decision],
            current=context,
            reflect_fn=failing_reflect_fn,
        )

        assert isinstance(result, DecisionBrief)
        assert result.recommendation.label == EpistemicLabel.RECOMMENDATION


class TestEdgeCases:
    def test_empty_decisions_list(self):
        recall = load_recall_bundle_kafka()
        context = load_context_nova()

        def empty_reflect_fn(question, scope, *, context=None):
            return ReflectResult(
                text=_minimal_synthesis_json(reconsideration=False),
                memory_ids=["mem-alpha-001"],
                source_refs=[SourceRef(source_id="SRC-ALPHA-001")],
            )

        result = build_decision_brief(
            query_id="test-empty-decisions",
            query="Should Nova use Kafka?",
            scope=_make_scope(),
            recall=recall,
            decisions=[],
            current=context,
            reflect_fn=empty_reflect_fn,
        )

        assert isinstance(result, DecisionBrief)
        assert result.drift is None
        assert result.reconsideration_warranted is False

    def test_missing_current_context(self):
        decision = load_decision_alpha_kafka()
        recall = load_recall_bundle_kafka()

        def reflect_fn(question, scope, *, context=None):
            return ReflectResult(
                text=_minimal_synthesis_json(reconsideration=False),
                memory_ids=["mem-alpha-001"],
                source_refs=[SourceRef(source_id="SRC-ALPHA-001")],
            )

        result = build_decision_brief(
            query_id="test-no-context",
            query="Tell me about the Alpha Kafka decision.",
            scope=_make_scope(),
            recall=recall,
            decisions=[decision],
            current=None,
            reflect_fn=reflect_fn,
        )

        assert isinstance(result, DecisionBrief)
        assert result.drift is not None
        assert result.drift.score == 0.0

    def test_malformed_llm_json_falls_back_to_deterministic(self):
        decision = load_decision_alpha_kafka()
        context = load_context_nova()
        recall = load_recall_bundle_kafka()

        def bad_json_reflect_fn(question, scope, *, context=None):
            return ReflectResult(
                text="I'm sorry, I can't help with that. Use Kafka!",
                memory_ids=["mem-alpha-001"],
                source_refs=[SourceRef(source_id="SRC-ALPHA-001")],
            )

        result = build_decision_brief(
            query_id="test-bad-json",
            query="Should Nova use Kafka?",
            scope=_make_scope(),
            recall=recall,
            decisions=[decision],
            current=context,
            reflect_fn=bad_json_reflect_fn,
        )

        assert isinstance(result, DecisionBrief)
        assert result.recommendation is not None
        assert result.recommendation.label == EpistemicLabel.RECOMMENDATION

    def test_uncited_claims_are_dropped(self):
        synthesis_with_uncited = json.dumps(
            {
                "answer_summary": "Test.",
                "historical_decisions": [
                    {
                        "text": "This claim has no refs.",
                        "label": "FACT",
                        "memory_ids": [],
                        "source_refs": [],
                    },
                    {
                        "text": "This claim has a ref.",
                        "label": "FACT",
                        "memory_ids": ["mem-alpha-001"],
                        "source_refs": [],
                    },
                ],
                "observations": [],
                "inferences": [],
                "recommendation": {
                    "text": "Original decision holds.",
                    "label": "RECOMMENDATION",
                    "memory_ids": [],
                    "source_refs": [],
                },
            }
        )

        decision = load_decision_alpha_kafka()
        context = load_context_nova()
        recall = load_recall_bundle_kafka()

        def reflect_fn(question, scope, *, context=None):
            return ReflectResult(
                text=synthesis_with_uncited,
                memory_ids=[],
                source_refs=[],
            )

        result = build_decision_brief(
            query_id="test-uncited",
            query="Test query.",
            scope=_make_scope(),
            recall=recall,
            decisions=[decision],
            current=context,
            reflect_fn=reflect_fn,
        )

        assert len(result.historical_decisions) == 1
        assert "has a ref" in result.historical_decisions[0].text

    def test_confidence_extraction_is_min_of_decisions(self):
        brief = build_fixture_brief_nova_kafka()
        decision = load_decision_alpha_kafka()
        assert brief.confidence.extraction == decision.extraction_confidence

    def test_confidence_retrieval_matches_recall_bundle(self):
        brief = build_fixture_brief_nova_kafka()
        recall = load_recall_bundle_kafka()
        assert brief.confidence.retrieval == recall.retrieval_confidence
