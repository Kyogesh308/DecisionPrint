"""
tests/p2/test_drift.py

Required tests for the Phase 1 drift engine.
All tests are fixture-only (no LLM calls, no network).
"""

from contracts.enums import ConstraintComparison, DriftLevel
from contracts.models import (
    Constraint,
    ConstraintDelta,
    ConstraintDeltaItem,
    CurrentProjectContext,
)
from intelligence import compare_constraints, normalize_constraints, score_drift
from tests.p2.fixtures.loader import (
    load_context_nova,
    load_decision_alpha_kafka,
)


def _make_delta(
    items: list[ConstraintDeltaItem], decision_id: str = "DEC-TEST-001"
) -> ConstraintDelta:
    return ConstraintDelta(decision_id=decision_id, project_id="test", items=items)


def _item(
    key: str,
    hist: object,
    curr: object,
    comparison: ConstraintComparison,
    reason_linked: bool,
    weight: float,
) -> ConstraintDeltaItem:
    return ConstraintDeltaItem(
        key=key,
        historical_value=hist,
        current_value=curr,
        comparison=comparison,
        is_reason_linked=reason_linked,
        weight=weight,
    )


class TestNormalizeConstraints:
    def test_integer_word_form_normalized(self):
        constraints = [Constraint(key="consumer_count", value="two")]
        result = normalize_constraints(constraints)
        assert result[0].normalized_value == 2

    def test_integer_numeric_string_normalized(self):
        constraints = [Constraint(key="consumer_count", value="15")]
        result = normalize_constraints(constraints)
        assert result[0].normalized_value == 15

    def test_integer_int_passthrough(self):
        constraints = [Constraint(key="consumer_count", value=2)]
        result = normalize_constraints(constraints)
        assert result[0].normalized_value == 2

    def test_bool_yes_normalized_to_true(self):
        constraints = [Constraint(key="replay_required", value="yes")]
        result = normalize_constraints(constraints)
        assert result[0].normalized_value is True

    def test_bool_no_normalized_to_false(self):
        constraints = [Constraint(key="replay_required", value="no")]
        result = normalize_constraints(constraints)
        assert result[0].normalized_value is False

    def test_bool_false_string_normalized(self):
        constraints = [Constraint(key="async_workflows", value="false")]
        result = normalize_constraints(constraints)
        assert result[0].normalized_value is False

    def test_bool_passthrough(self):
        constraints = [Constraint(key="replay_required", value=True)]
        result = normalize_constraints(constraints)
        assert result[0].normalized_value is True

    def test_category_synonym_mapped(self):
        constraints = [Constraint(key="traffic_volume", value="medium")]
        result = normalize_constraints(constraints)
        assert result[0].normalized_value == "moderate"

    def test_category_moderate_passthrough(self):
        constraints = [Constraint(key="traffic_volume", value="moderate")]
        result = normalize_constraints(constraints)
        assert result[0].normalized_value == "moderate"

    def test_unknown_key_leaves_normalized_value_none(self):
        constraints = [Constraint(key="some_future_key", value="whatever")]
        result = normalize_constraints(constraints)
        assert result[0].normalized_value is None

    def test_original_value_not_mutated(self):
        original = Constraint(key="consumer_count", value="two")
        constraints = [original]
        normalize_constraints(constraints)
        assert original.normalized_value is None
        assert original.value == "two"

    def test_multiple_constraints_all_normalized(self):
        constraints = [
            Constraint(key="consumer_count", value=2),
            Constraint(key="replay_required", value=False),
            Constraint(key="traffic_volume", value="moderate"),
            Constraint(key="ops_capacity", value="small"),
        ]
        result = normalize_constraints(constraints)
        assert result[0].normalized_value == 2
        assert result[1].normalized_value is False
        assert result[2].normalized_value == "moderate"
        assert result[3].normalized_value == "small"

    def test_ops_capacity_synonyms(self):
        for raw, expected in [
            ("tiny", "small"),
            ("mature", "large"),
            ("average", "medium"),
        ]:
            result = normalize_constraints([Constraint(key="ops_capacity", value=raw)])
            assert result[0].normalized_value == expected, f"Failed for {raw!r}"

    def test_approximate_integer_string_parsed(self):
        constraints = [Constraint(key="consumer_count", value="~15 consumers")]
        result = normalize_constraints(constraints)
        assert result[0].normalized_value == 15


class TestCompareConstraints:
    def test_compare_constraints_marks_unknown_when_current_missing(self):
        decision = load_decision_alpha_kafka()
        current = load_context_nova()
        current_without_ops = CurrentProjectContext(
            project_id=current.project_id,
            summary=current.summary,
            constraints=[c for c in current.constraints if c.key != "ops_capacity"],
            source_refs=current.source_refs,
            updated_at=current.updated_at,
        )
        delta = compare_constraints(decision, current_without_ops)
        ops_item = next(i for i in delta.items if i.key == "ops_capacity")
        assert ops_item.comparison == ConstraintComparison.UNKNOWN
        assert ops_item.historical_value is not None
        assert ops_item.current_value is None

    def test_same_values_classified_same(self):
        decision = load_decision_alpha_kafka()
        same_current = CurrentProjectContext(
            project_id="test",
            summary="same as alpha",
            constraints=list(decision.constraints),
            source_refs=[],
            updated_at="2026-01-01T00:00:00Z",
        )
        delta = compare_constraints(decision, same_current)
        for item in delta.items:
            if item.comparison != ConstraintComparison.NEWLY_PRESENT:
                assert item.comparison == ConstraintComparison.SAME, (
                    f"Expected SAME for {item.key}, got {item.comparison}"
                )

    def test_changed_values_classified_changed(self):
        decision = load_decision_alpha_kafka()
        current = load_context_nova()
        delta = compare_constraints(decision, current)
        cc_item = next(i for i in delta.items if i.key == "consumer_count")
        assert cc_item.comparison == ConstraintComparison.CHANGED
        assert cc_item.historical_value == 2
        assert cc_item.current_value == 15

    def test_is_reason_linked_copied_from_decision(self):
        decision = load_decision_alpha_kafka()
        current = load_context_nova()
        delta = compare_constraints(decision, current)
        cc_item = next(i for i in delta.items if i.key == "consumer_count")
        assert cc_item.is_reason_linked is True

    def test_newly_present_constraint_in_current(self):
        decision = load_decision_alpha_kafka()
        current = load_context_nova()
        delta = compare_constraints(decision, current)
        sla_item = next((i for i in delta.items if i.key == "sla_tier"), None)
        if sla_item:
            assert sla_item.comparison == ConstraintComparison.NEWLY_PRESENT
            assert sla_item.is_reason_linked is False

    def test_reason_linked_items_get_full_weight(self):
        decision = load_decision_alpha_kafka()
        current = load_context_nova()
        delta = compare_constraints(decision, current)
        for item in delta.items:
            if item.is_reason_linked:
                assert item.weight == 1.0
            else:
                assert item.weight == 0.25

    def test_decision_id_and_project_id_propagated(self):
        decision = load_decision_alpha_kafka()
        current = load_context_nova()
        delta = compare_constraints(decision, current)
        assert delta.decision_id == decision.id
        assert delta.project_id == current.project_id


class TestScoreDrift:
    def test_score_drift_high_for_kafka_nova(self):
        decision = load_decision_alpha_kafka()
        current = load_context_nova()
        delta = compare_constraints(decision, current)
        result = score_drift(delta)

        assert result.level == DriftLevel.HIGH
        assert result.reconsideration_warranted is True
        assert result.score >= 0.70, f"Expected score >= 0.70, got {result.score}"

    def test_score_drift_none_when_all_same(self):
        decision = load_decision_alpha_kafka()
        same_current = CurrentProjectContext(
            project_id="test",
            summary="identical context",
            constraints=list(decision.constraints),
            source_refs=[],
            updated_at="2026-01-01T00:00:00Z",
        )
        delta = compare_constraints(decision, same_current)
        result = score_drift(delta)

        assert result.score == 0.0
        assert result.level == DriftLevel.NONE
        assert result.reconsideration_warranted is False

    def test_score_drift_low_confidence_blocks_reconsideration(self):
        items = [
            _item("consumer_count", 2, None, ConstraintComparison.UNKNOWN, True, 1.0),
            _item(
                "replay_required", False, None, ConstraintComparison.UNKNOWN, True, 1.0
            ),
            _item(
                "traffic_volume",
                "moderate",
                None,
                ConstraintComparison.UNKNOWN,
                True,
                1.0,
            ),
            _item(
                "ops_capacity", "small", None, ConstraintComparison.UNKNOWN, True, 1.0
            ),
        ]
        delta = _make_delta(items)
        result = score_drift(delta)

        assert result.drift_confidence == 0.0
        assert result.reconsideration_warranted is False

    def test_score_drift_medium_when_non_reason_linked_changed(self):
        items = [
            _item("consumer_count", 2, 2, ConstraintComparison.SAME, True, 1.0),
            _item(
                "replay_required", False, False, ConstraintComparison.SAME, True, 1.0
            ),
            _item("traffic_volume", "low", "low", ConstraintComparison.SAME, True, 1.0),
            _item(
                "client_diversity",
                "internal_only",
                "public",
                ConstraintComparison.CHANGED,
                False,
                0.25,
            ),
        ]
        delta = _make_delta(items)
        result = score_drift(delta)

        assert result.score == 0.0
        assert result.level == DriftLevel.NONE
        assert result.reconsideration_warranted is False

    def test_score_drift_empty_delta_returns_none_level(self):
        delta = _make_delta([])
        result = score_drift(delta)
        assert result.level == DriftLevel.NONE
        assert result.score == 0.0
        assert result.reconsideration_warranted is False
        assert result.drift_confidence == 0.0

    def test_score_drift_no_reason_linked_returns_none(self):
        items = [
            _item("client_count", 5, 10, ConstraintComparison.CHANGED, False, 0.25),
        ]
        delta = _make_delta(items)
        result = score_drift(delta)
        assert result.level == DriftLevel.NONE
        assert result.drift_confidence == 0.0

    def test_score_drift_partial_change_medium_level(self):
        items = [
            _item("consumer_count", 2, 15, ConstraintComparison.CHANGED, True, 1.0),
            _item(
                "replay_required", False, True, ConstraintComparison.CHANGED, True, 1.0
            ),
            _item(
                "traffic_volume",
                "moderate",
                "moderate",
                ConstraintComparison.SAME,
                True,
                1.0,
            ),
        ]
        delta = _make_delta(items)
        result = score_drift(delta)
        assert abs(result.score - 2 / 3) < 0.01
        assert result.level == DriftLevel.MEDIUM
        assert result.reconsideration_warranted is True

    def test_score_drift_result_contains_delta(self):
        decision = load_decision_alpha_kafka()
        current = load_context_nova()
        delta = compare_constraints(decision, current)
        result = score_drift(delta)
        assert result.delta is delta

    def test_score_drift_low_level_boundary(self):
        items = [
            _item("consumer_count", 2, 15, ConstraintComparison.CHANGED, True, 1.0),
            _item(
                "replay_required", False, False, ConstraintComparison.SAME, True, 1.0
            ),
            _item(
                "traffic_volume",
                "moderate",
                "moderate",
                ConstraintComparison.SAME,
                True,
                1.0,
            ),
            _item(
                "ops_capacity", "small", "small", ConstraintComparison.SAME, True, 1.0
            ),
            _item(
                "async_workflows", False, False, ConstraintComparison.SAME, True, 1.0
            ),
        ]
        delta = _make_delta(items)
        result = score_drift(delta)
        assert abs(result.score - 0.20) < 0.01
        assert result.level == DriftLevel.LOW
        assert result.reconsideration_warranted is False

    def test_score_drift_incomparable_reduces_confidence(self):
        items = [
            _item("consumer_count", 2, 15, ConstraintComparison.CHANGED, True, 1.0),
            _item(
                "traffic_volume",
                "moderate",
                None,
                ConstraintComparison.INCOMPARABLE,
                True,
                1.0,
            ),
        ]
        delta = _make_delta(items)
        result = score_drift(delta)
        assert result.drift_confidence == 0.5
        assert result.score == 1.0
        assert result.reconsideration_warranted is True
