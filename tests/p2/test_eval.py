"""
Tests for Phase 5 evaluation harness.
No LLM calls. No file I/O beyond small temp files.
"""
from __future__ import annotations

import json
import pytest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

from contracts.enums import DriftLevel, CausalLabel, DecisionStatus
from contracts.models import (
    BriefClaim, CausalLink, Constraint, ConfidenceBreakdown,
    Decision, DriftResult, Outcome, RecalledMemory, SourceRef,
)
from contracts.enums import EpistemicLabel, MemoryKind
from eval.baseline import run_baseline_rag, clear_chunk_cache
from eval.metrics import (
    compute_attribution_metrics,
    compute_causal_metrics,
    compute_drift_f1,
    score_extraction,
)
from eval.models import EvaluationReport


# --------------------------------------------------------------------------- #
# Helpers                                                                       #
# --------------------------------------------------------------------------- #

def _make_decision(
    id: str = "DEC-ALPHA-001",
    project_id: str = "alpha",
    statement: str = "The team decided to reject Kafka in favour of Redis Streams.",
    constraints: list[Constraint] | None = None,
) -> Decision:
    from contracts.models import Reason
    return Decision(
        id=id,
        project_id=project_id,
        title="Reject Kafka",
        decision_statement=statement,
        occurred_at=datetime(2025, 3, 14, tzinfo=timezone.utc),
        participants=["alice"],
        context_summary="Low consumer count project.",
        constraints=constraints or [
            Constraint(key="consumer_count", value="2", is_reason_linked=True),
            Constraint(key="replay_required", value="false", is_reason_linked=True),
            Constraint(key="traffic_volume", value="moderate", is_reason_linked=True),
        ],
        assumptions=[],
        alternatives=[],
        selected_option="Redis Streams",
        reasons=[Reason(statement="Low consumer count.", source_memory_id=None)],
        technologies=["Redis Streams"],
        source_refs=[],
        extraction_confidence=0.88,
        outcome_refs=[],
        status=DecisionStatus.active,
        superseded_by=None,
        related_decisions=[],
        needs_review=False,
    )


def _make_brief(*, cited: bool = True) -> object:
    """Make a minimal DecisionBrief-like object for attribution tests."""
    ref = SourceRef(source_id="SRC-ALPHA-001", document_id="doc-001") if cited else None
    refs = [ref] if ref else []
    mids = ["mem-001"] if cited else []

    from contracts.models import DecisionBrief

    return DecisionBrief(
        query_id="Q-TEST",
        query="test question",
        project_id="nova",
        answer_summary="answer",
        historical_decisions=[
            BriefClaim(text="Fact 1", label=EpistemicLabel.FACT, source_refs=refs, memory_ids=mids)
        ],
        historical_constraints=[],
        current_constraints=[],
        constraint_differences=[],
        observations=[],
        inferences=[
            BriefClaim(text="Inference 1", label=EpistemicLabel.INFERENCE, source_refs=refs, memory_ids=mids)
        ],
        drift=None,
        reconsideration_warranted=False,
        recommendation=BriefClaim(
            text="Recommend", label=EpistemicLabel.RECOMMENDATION, source_refs=refs, memory_ids=mids
        ),
        confidence=ConfidenceBreakdown(),
        sources=refs,
        generated_at=datetime.now(tz=timezone.utc).isoformat(),
    )


# --------------------------------------------------------------------------- #
# score_extraction tests                                                        #
# --------------------------------------------------------------------------- #

class TestScoreExtraction:

    def test_perfect_match_returns_ones(self):
        decision = _make_decision()
        scores = score_extraction([decision], [decision])

        assert scores["statement_accuracy"] == pytest.approx(1.0)
        assert scores["constraint_precision"] == pytest.approx(1.0)
        assert scores["constraint_recall"] == pytest.approx(1.0)
        assert scores["constraint_f1"] == pytest.approx(1.0)

    def test_empty_gold_returns_zeros(self):
        decision = _make_decision()
        scores = score_extraction([decision], [])

        assert scores["statement_accuracy"] == 0.0

    def test_missing_prediction_reduces_recall(self):
        gold = [_make_decision(id="DEC-A-001"), _make_decision(id="DEC-A-002", project_id="beta")]
        predicted = [_make_decision(id="DEC-A-001")]

        scores = score_extraction(predicted, gold)

        # One decision missing → recall drops
        assert scores["constraint_recall"] < 1.0

    def test_extra_constraint_reduces_precision(self):
        gold = _make_decision(constraints=[
            Constraint(key="consumer_count", value="2", is_reason_linked=True),
        ])
        pred = _make_decision(constraints=[
            Constraint(key="consumer_count", value="2", is_reason_linked=True),
            Constraint(key="ops_capacity", value="small", is_reason_linked=False),
        ])
        scores = score_extraction([pred], [gold])

        assert scores["constraint_precision"] < 1.0
        assert scores["constraint_recall"] == pytest.approx(1.0)

    def test_wrong_value_reduces_constraint_scores(self):
        gold = _make_decision(constraints=[
            Constraint(key="consumer_count", value="2", is_reason_linked=True),
        ])
        pred = _make_decision(constraints=[
            Constraint(key="consumer_count", value="15", is_reason_linked=True),
        ])
        scores = score_extraction([pred], [gold])

        # Different value → constraint precision and recall both drop
        assert scores["constraint_precision"] < 1.0
        assert scores["constraint_recall"] < 1.0

    def test_reason_linked_accuracy_correct(self):
        gold = _make_decision(constraints=[
            Constraint(key="consumer_count", value="2", is_reason_linked=True),
            Constraint(key="ops_capacity", value="small", is_reason_linked=False),
        ])
        pred = _make_decision(constraints=[
            Constraint(key="consumer_count", value="2", is_reason_linked=True),
            Constraint(key="ops_capacity", value="small", is_reason_linked=False),
        ])
        scores = score_extraction([pred], [gold])

        assert scores["reason_linked_accuracy"] == pytest.approx(1.0)

    def test_reason_linked_accuracy_wrong_flag(self):
        gold = _make_decision(constraints=[
            Constraint(key="consumer_count", value="2", is_reason_linked=True),
        ])
        pred = _make_decision(constraints=[
            Constraint(key="consumer_count", value="2", is_reason_linked=False),  # wrong
        ])
        scores = score_extraction([pred], [gold])

        assert scores["reason_linked_accuracy"] < 1.0


# --------------------------------------------------------------------------- #
# compute_drift_f1 tests                                                        #
# --------------------------------------------------------------------------- #

class TestComputeDriftF1:

    def test_perfect_prediction_returns_one(self):
        cases = [
            {"predicted_level": "high", "gold_level": "high"},
            {"predicted_level": "none", "gold_level": "none"},
            {"predicted_level": "medium", "gold_level": "medium"},
            {"predicted_level": "low", "gold_level": "low"},
        ]
        result = compute_drift_f1(cases)
        assert result == pytest.approx(1.0)

    def test_all_wrong_returns_low_f1(self):
        cases = [
            {"predicted_level": "none", "gold_level": "high"},
            {"predicted_level": "none", "gold_level": "medium"},
        ]
        result = compute_drift_f1(cases)
        assert result < 0.5

    def test_empty_cases_returns_zero(self):
        result = compute_drift_f1([])
        assert result == 0.0

    def test_unknown_label_treated_as_none(self):
        cases = [{"predicted_level": "GARBAGE_VALUE", "gold_level": "none"}]
        result = compute_drift_f1(cases)
        # Both become "none" after normalization → should match
        assert result == pytest.approx(1.0)

    def test_partial_correct(self):
        cases = [
            {"predicted_level": "high", "gold_level": "high"},
            {"predicted_level": "high", "gold_level": "none"},  # wrong
        ]
        result = compute_drift_f1(cases)
        # macro F1 across 4 classes with 1 TP for high, 1 FP for high, 1 FN for none
        assert 0.0 < result < 1.0


# --------------------------------------------------------------------------- #
# attribution metrics tests                                                     #
# --------------------------------------------------------------------------- #

class TestAttributionMetrics:

    def test_fully_cited_brief_has_zero_hallucination(self):
        brief = _make_brief(cited=True)
        result = compute_attribution_metrics([brief])

        assert result.attribution_rate == pytest.approx(1.0)
        assert result.hallucination_rate == pytest.approx(0.0)

    def test_uncited_brief_has_full_hallucination(self):
        brief = _make_brief(cited=False)
        result = compute_attribution_metrics([brief])

        assert result.hallucination_rate == pytest.approx(1.0)
        assert result.attribution_rate == pytest.approx(0.0)

    def test_empty_briefs_returns_defaults(self):
        result = compute_attribution_metrics([])
        assert result.attribution_rate == pytest.approx(1.0)  # vacuously correct
        assert result.n_claims_evaluated == 0

    def test_mixed_briefs_gives_partial_rate(self):
        cited = _make_brief(cited=True)
        uncited = _make_brief(cited=False)
        result = compute_attribution_metrics([cited, uncited])

        assert 0.0 < result.attribution_rate < 1.0
        assert 0.0 < result.hallucination_rate < 1.0


# --------------------------------------------------------------------------- #
# causal metrics tests                                                          #
# --------------------------------------------------------------------------- #

class TestCausalMetrics:

    def test_perfect_causal_match(self):
        gold = [{"decision_id": "DEC-CEDAR-001", "outcome_id": "OUT-CEDAR-001", "gold_label": "explicit_causal_link"}]
        predicted = [{"decision_id": "DEC-CEDAR-001", "outcome_id": "OUT-CEDAR-001", "label": "explicit_causal_link"}]
        result = compute_causal_metrics(predicted, gold)
        assert result.label_accuracy == pytest.approx(1.0)

    def test_wrong_causal_label(self):
        gold = [{"decision_id": "DEC-CEDAR-001", "outcome_id": "OUT-CEDAR-001", "gold_label": "explicit_causal_link"}]
        predicted = [{"decision_id": "DEC-CEDAR-001", "outcome_id": "OUT-CEDAR-001", "label": "none"}]
        result = compute_causal_metrics(predicted, gold)
        assert result.label_accuracy == pytest.approx(0.0)

    def test_unmatched_prediction_ignored(self):
        gold = [{"decision_id": "DEC-A-001", "outcome_id": "OUT-A-001", "gold_label": "none"}]
        predicted = [{"decision_id": "DEC-DIFFERENT-001", "outcome_id": "OUT-A-001", "label": "none"}]
        result = compute_causal_metrics(predicted, gold)
        assert result.n_cases_evaluated == 0


# --------------------------------------------------------------------------- #
# baseline RAG tests                                                            #
# --------------------------------------------------------------------------- #

class TestBaselineRag:

    def setup_method(self):
        clear_chunk_cache()

    def test_returns_string(self, tmp_path):
        doc = tmp_path / "test_doc.md"
        doc.write_text("The team decided to reject Kafka because consumer count was two.")

        result = run_baseline_rag("Why was Kafka rejected?", data_dir=str(tmp_path))

        assert isinstance(result, str)

    def test_relevant_chunk_surfaces_for_kafka_query(self, tmp_path):
        doc = tmp_path / "alpha_adr.md"
        doc.write_text(
            "Architecture decision: reject Kafka for Alpha project. "
            "Consumer count is two. No replay required. Team is small. "
            "Redis Streams was selected instead."
        )
        irrelevant = tmp_path / "unrelated.md"
        irrelevant.write_text("This is about the company picnic and lunch catering.")

        result = run_baseline_rag("Why was Kafka rejected?", data_dir=str(tmp_path))

        assert "kafka" in result.lower() or "alpha" in result.lower()

    def test_empty_data_dir_returns_empty_string(self, tmp_path):
        result = run_baseline_rag("any question", data_dir=str(tmp_path))
        assert result == ""

    def test_nonexistent_data_dir_returns_empty_string(self):
        result = run_baseline_rag("any question", data_dir="/nonexistent/path/xyz")
        assert result == ""

    def test_gold_files_excluded(self, tmp_path):
        gold_dir = tmp_path / "gold"
        gold_dir.mkdir()
        gold_file = gold_dir / "eval_questions.json"
        gold_file.write_text(json.dumps([{"question": "test"}]))

        real_doc = tmp_path / "doc.md"
        real_doc.write_text("Real organizational document about decisions.")

        result = run_baseline_rag("test question", data_dir=str(tmp_path))

        # gold/ content should not appear in retrieved chunks
        assert "eval_questions" not in result

    def test_chunk_cache_populated_after_first_call(self, tmp_path):
        from eval.baseline import _chunk_cache
        doc = tmp_path / "doc.md"
        doc.write_text("Some content about decisions and constraints.")

        run_baseline_rag("question", data_dir=str(tmp_path))

        assert str(tmp_path) in _chunk_cache

    def test_top_k_limits_chunks_returned(self, tmp_path):
        for i in range(10):
            (tmp_path / f"doc_{i}.md").write_text(
                f"Document {i} about Kafka and decisions and constraints. " * 5
            )
        result_k1 = run_baseline_rag("Kafka", data_dir=str(tmp_path), top_k=1)
        result_k3 = run_baseline_rag("Kafka", data_dir=str(tmp_path), top_k=3)

        # k=3 should contain at least as much text as k=1 (more chunks)
        assert len(result_k3) >= len(result_k1)
