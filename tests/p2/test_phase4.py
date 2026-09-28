"""
Tests for Phase 4: extract_current_context, extract_outcomes, classify_causal_link.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import patch

import pytest

from contracts.enums import (
    CausalLabel,
    DecisionStatus,
    MemoryKind,
)
from contracts.models import (
    Constraint,
    CurrentProjectContext,
    Decision,
    Outcome,
    RecalledMemory,
    RetainResult,
    SourceManifestEntry,
)
from intelligence import (
    classify_causal_link,
    extract_current_context,
    extract_outcomes,
)
from intelligence._id_counter import reset_counters_for_testing

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture(autouse=True)
def reset_ids():
    reset_counters_for_testing()
    yield
    reset_counters_for_testing()


# --------------------------------------------------------------------------- #
# Shared fixture builders                                                       #
# --------------------------------------------------------------------------- #


def _load_source(filename: str) -> SourceManifestEntry:
    return SourceManifestEntry(**json.loads((FIXTURES / filename).read_text()))


def _make_retained(
    source_id: str, memory_ids: list[str], texts: list[str] | None = None
) -> RetainResult:
    texts = texts or [f"Retained fact {mid}" for mid in memory_ids]
    memories = [
        RecalledMemory(
            memory_id=mid,
            kind=MemoryKind.experience,
            text=text,
            tags=[],
            entities=[],
            source_refs=[],
            relevance=1.0,
        )
        for mid, text in zip(memory_ids, texts)
    ]
    return RetainResult(
        source_id=source_id,
        document_id=f"doc-{source_id.lower()}",
        memory_ids=memory_ids,
        memories=memories,
    )


def _make_cedar_decision() -> Decision:
    from contracts.models import Reason

    return Decision(
        id="DEC-CEDAR-001",
        project_id="cedar",
        title="Disable automated backups to reduce storage costs",
        decision_statement="Automated backups were disabled to reduce storage costs.",
        occurred_at=datetime(2025, 1, 15, tzinfo=UTC),
        participants=["ops-lead"],
        context_summary="Budget pressure required cost reduction.",
        constraints=[
            Constraint(key="backup_policy", value="none", is_reason_linked=True),
            Constraint(key="budget_pressure", value="high", is_reason_linked=True),
        ],
        assumptions=[],
        alternatives=[],
        selected_option="disable backups",
        reasons=[
            Reason(statement="Storage costs exceeded budget.", source_memory_id=None),
        ],
        technologies=[],
        source_refs=[],
        extraction_confidence=0.87,
        outcome_refs=[],
        status=DecisionStatus.active,
        superseded_by=None,
        related_decisions=[],
        needs_review=False,
    )


def _make_cedar_outcome() -> Outcome:
    return Outcome(
        outcome_id="OUT-CEDAR-001",
        project_id="cedar",
        occurred_at=datetime(2025, 11, 3, tzinfo=UTC),
        statement="Recovery took 14 hours due to absence of automated backups.",
        source_refs=[],
        decision_ids=[],
        causal_label=CausalLabel.NONE,
        confidence=0.75,
    )


def _make_cedar_evidence(strong: bool = True) -> list[RecalledMemory]:
    texts = (
        [
            "The postmortem explicitly identifies the decision to disable automated "
            "backups as the primary contributing factor to the extended recovery window.",
            "Backup configuration was set to 'disabled' in the deployment manifest, "
            "consistent with the decision made in Q1 2025.",
        ]
        if strong
        else ["The Cedar project experienced a storage incident in November 2025."]
    )
    ids = [f"mem-cedar-{i:03d}" for i in range(1, len(texts) + 1)]
    return [
        RecalledMemory(
            memory_id=mid,
            kind=MemoryKind.experience,
            text=text,
            tags=[],
            entities=[],
            source_refs=[],
            relevance=0.9,
        )
        for mid, text in zip(ids, texts)
    ]


# --------------------------------------------------------------------------- #
# extract_current_context                                                       #
# --------------------------------------------------------------------------- #


class TestExtractCurrentContextNova:
    def test_returns_current_project_context_type(self):
        source = _load_source("source_nova_transcript.json")
        text = (FIXTURES / "text_nova_transcript.txt").read_text()
        retained = _make_retained("SRC-NOVA-001", ["mem-nova-001", "mem-nova-002"])

        result = extract_current_context(source, text, retained)

        assert isinstance(result, CurrentProjectContext)

    def test_project_id_from_source_not_llm(self):
        """project_id must always come from the SourceManifestEntry, not the LLM."""
        source = _load_source("source_nova_transcript.json")
        text = (FIXTURES / "text_nova_transcript.txt").read_text()
        retained = _make_retained("SRC-NOVA-001", ["mem-nova-001"])

        result = extract_current_context(source, text, retained)

        assert result.project_id == "nova"

    def test_consumer_count_15_extracted(self):
        """Phase 4 exit criterion: Nova must have consumer_count=15."""
        source = _load_source("source_nova_transcript.json")
        text = (FIXTURES / "text_nova_transcript.txt").read_text()
        retained = _make_retained("SRC-NOVA-001", ["mem-nova-001", "mem-nova-002"])

        result = extract_current_context(source, text, retained)
        constraint_map = {c.key: c for c in result.constraints}

        assert "consumer_count" in constraint_map
        assert str(constraint_map["consumer_count"].value) == "15"

    def test_replay_required_true(self):
        """Phase 4 exit criterion: replay_required must be True."""
        source = _load_source("source_nova_transcript.json")
        text = (FIXTURES / "text_nova_transcript.txt").read_text()
        retained = _make_retained("SRC-NOVA-001", ["mem-nova-001"])

        result = extract_current_context(source, text, retained)
        constraint_map = {c.key: c for c in result.constraints}

        assert "replay_required" in constraint_map
        assert str(constraint_map["replay_required"].value).lower() in (
            "true",
            "yes",
            "1",
        )

    def test_traffic_volume_high(self):
        source = _load_source("source_nova_transcript.json")
        text = (FIXTURES / "text_nova_transcript.txt").read_text()
        retained = _make_retained("SRC-NOVA-001", ["mem-nova-001"])

        result = extract_current_context(source, text, retained)
        constraint_map = {c.key: c for c in result.constraints}

        assert "traffic_volume" in constraint_map
        assert str(constraint_map["traffic_volume"].value).lower() == "high"

    def test_is_reason_linked_always_false_on_context(self):
        """is_reason_linked must always be False on current context constraints."""
        source = _load_source("source_nova_transcript.json")
        text = (FIXTURES / "text_nova_transcript.txt").read_text()
        retained = _make_retained("SRC-NOVA-001", ["mem-nova-001"])

        result = extract_current_context(source, text, retained)

        for c in result.constraints:
            assert c.is_reason_linked is False, (
                f"Constraint '{c.key}' has is_reason_linked=True on current context — must be False"
            )

    def test_unknown_constraint_keys_dropped(self):
        """Non-canonical keys must be silently dropped from current context."""
        source = _load_source("source_nova_transcript.json")
        retained = _make_retained("SRC-NOVA-001", [])

        # Patch LLM to return a response with one valid and one invalid key
        from pydantic import BaseModel

        class _FakeResult(BaseModel):
            project_id: str
            summary: str
            constraints: list[dict]
            extraction_confidence: float

        fake = _FakeResult(
            project_id="nova",
            summary="test",
            constraints=[
                {
                    "key": "consumer_count",
                    "value": "15",
                    "unit": None,
                    "source_memory_id": None,
                },
                {
                    "key": "made_up_key",
                    "value": "whatever",
                    "unit": None,
                    "source_memory_id": None,
                },
            ],
            extraction_confidence=0.8,
        )

        with patch("intelligence.context.call_llm_json", return_value=fake):
            result = extract_current_context(source, "text", retained)

        keys = {c.key for c in result.constraints}
        assert "consumer_count" in keys
        assert "made_up_key" not in keys

    def test_empty_source_text_returns_empty_context(self):
        source = _load_source("source_nova_transcript.json")
        retained = _make_retained("SRC-NOVA-001", [])

        result = extract_current_context(source, "   ", retained)

        assert isinstance(result, CurrentProjectContext)
        assert result.constraints == []

    def test_source_ref_populated(self):
        source = _load_source("source_nova_transcript.json")
        text = (FIXTURES / "text_nova_transcript.txt").read_text()
        retained = _make_retained("SRC-NOVA-001", ["mem-nova-001"])

        result = extract_current_context(source, text, retained)

        assert len(result.source_refs) == 1
        assert result.source_refs[0].source_id == "SRC-NOVA-001"


# --------------------------------------------------------------------------- #
# extract_outcomes                                                              #
# --------------------------------------------------------------------------- #


class TestExtractOutcomesCedar:
    def test_returns_list_of_outcomes(self):
        source = _load_source("source_cedar_postmortem.json")
        text = (FIXTURES / "text_cedar_postmortem.txt").read_text()
        retained = _make_retained("SRC-CEDAR-002", ["mem-cedar-001", "mem-cedar-002"])

        outcomes = extract_outcomes(source, text, retained)

        assert isinstance(outcomes, list)
        assert len(outcomes) >= 1

    def test_outcome_id_format(self):
        source = _load_source("source_cedar_postmortem.json")
        text = (FIXTURES / "text_cedar_postmortem.txt").read_text()
        retained = _make_retained("SRC-CEDAR-002", ["mem-cedar-001"])

        outcomes = extract_outcomes(source, text, retained)

        assert outcomes[0].outcome_id == "OUT-CEDAR-001"

    def test_decision_ids_always_empty(self):
        """
        decision_ids must always be [] on return from extract_outcomes.
        The causal classifier links them — not this function.
        """
        source = _load_source("source_cedar_postmortem.json")
        text = (FIXTURES / "text_cedar_postmortem.txt").read_text()
        retained = _make_retained("SRC-CEDAR-002", ["mem-cedar-001"])

        outcomes = extract_outcomes(source, text, retained)

        for outcome in outcomes:
            assert outcome.decision_ids == [], (
                f"Outcome {outcome.outcome_id} has non-empty decision_ids — must be []"
            )

    def test_outcome_statement_populated(self):
        source = _load_source("source_cedar_postmortem.json")
        text = (FIXTURES / "text_cedar_postmortem.txt").read_text()
        retained = _make_retained("SRC-CEDAR-002", ["mem-cedar-001"])

        outcomes = extract_outcomes(source, text, retained)

        assert len(outcomes[0].statement) > 0

    def test_empty_text_returns_empty_list(self):
        source = _load_source("source_cedar_postmortem.json")
        retained = _make_retained("SRC-CEDAR-002", [])

        outcomes = extract_outcomes(source, "  ", retained)

        assert outcomes == []


# --------------------------------------------------------------------------- #
# classify_causal_link                                                          #
# --------------------------------------------------------------------------- #


class TestClassifyCausalLinkCedar:
    def test_explicit_causal_link_with_strong_evidence(self):
        """
        Phase 4 exit criterion: Cedar postmortem must classify as explicit_causal_link
        with at least one cited evidence ID.
        """
        decision = _make_cedar_decision()
        outcome = _make_cedar_outcome()
        evidence = _make_cedar_evidence(strong=True)

        result = classify_causal_link(decision, outcome, evidence)

        assert result.label == CausalLabel.EXPLICIT_CAUSAL_LINK
        assert len(result.evidence_ids) >= 1
        assert result.decision_id == "DEC-CEDAR-001"
        assert result.outcome_id == "OUT-CEDAR-001"

    def test_evidence_ids_are_from_provided_evidence(self):
        """evidence_ids in result must all come from the provided evidence list."""
        decision = _make_cedar_decision()
        outcome = _make_cedar_outcome()
        evidence = _make_cedar_evidence(strong=True)
        valid_ids = {m.memory_id for m in evidence}

        result = classify_causal_link(decision, outcome, evidence)

        for eid in result.evidence_ids:
            assert eid in valid_ids, f"evidence_id '{eid}' not in provided evidence"

    def test_weak_overlap_returns_possible_or_none(self):
        """
        Weak evidence (entity/time overlap only) should return
        possible_causal_link or none — never explicit or strong.
        """
        decision = _make_cedar_decision()
        outcome = _make_cedar_outcome()
        outcome.outcome_id = "OUT-CEDAR-WEAK"
        evidence = _make_cedar_evidence(strong=False)

        result = classify_causal_link(decision, outcome, evidence)

        assert result.label in (
            CausalLabel.POSSIBLE_CAUSAL_LINK,
            CausalLabel.NONE,
        ), f"Expected possible or none, got {result.label}"

    def test_no_evidence_returns_none(self):
        """Hard rule: empty evidence list must always return CausalLabel.NONE."""
        decision = _make_cedar_decision()
        outcome = _make_cedar_outcome()

        result = classify_causal_link(decision, outcome, evidence=[])

        assert result.label == CausalLabel.NONE
        assert result.evidence_ids == []

    def test_hallucinated_evidence_ids_downgrade_to_none(self):
        """
        If the LLM returns evidence_ids not in the provided evidence list,
        the label must be downgraded to none.
        """
        decision = _make_cedar_decision()
        outcome = _make_cedar_outcome()
        evidence = [
            RecalledMemory(
                memory_id="mem-real-001",
                kind=MemoryKind.experience,
                text="Real evidence.",
                tags=[],
                entities=[],
                source_refs=[],
                relevance=0.8,
            )
        ]

        from pydantic import BaseModel

        class _FakeClassification(BaseModel):
            label: str
            rationale: str
            evidence_ids: list[str]
            confidence: float

        fake = _FakeClassification(
            label="explicit_causal_link",
            rationale="The decision caused the outcome.",
            evidence_ids=["mem-hallucinated-999"],  # doesn't exist
            confidence=0.95,
        )

        with patch("intelligence.causal.call_llm_json", return_value=fake):
            result = classify_causal_link(decision, outcome, evidence)

        assert result.label == CausalLabel.NONE
        assert result.evidence_ids == []

    def test_strong_evidence_requires_two_ids(self):
        """strong_evidence with only one verified ID must downgrade to none."""
        decision = _make_cedar_decision()
        outcome = _make_cedar_outcome()
        evidence = [
            RecalledMemory(
                memory_id="mem-cedar-001",
                kind=MemoryKind.experience,
                text="Single piece of supporting evidence.",
                tags=[],
                entities=[],
                source_refs=[],
                relevance=0.7,
            )
        ]

        from pydantic import BaseModel

        class _FakeClassification(BaseModel):
            label: str
            rationale: str
            evidence_ids: list[str]
            confidence: float

        fake = _FakeClassification(
            label="strong_evidence",
            rationale="Multiple sources support this.",
            evidence_ids=["mem-cedar-001"],  # only 1 — strong_evidence requires 2
            confidence=0.80,
        )

        with patch("intelligence.causal.call_llm_json", return_value=fake):
            result = classify_causal_link(decision, outcome, evidence)

        assert result.label == CausalLabel.NONE

    def test_llm_failure_returns_none_not_raises(self):
        """classify_causal_link must never raise — LLM failure returns NONE."""
        from intelligence.llm import LLMUnavailableError

        decision = _make_cedar_decision()
        outcome = _make_cedar_outcome()
        evidence = _make_cedar_evidence(strong=True)

        with patch(
            "intelligence.causal.call_llm_json",
            side_effect=LLMUnavailableError("timeout"),
        ):
            result = classify_causal_link(decision, outcome, evidence)

        assert result.label == CausalLabel.NONE

    def test_rationale_populated_on_explicit_link(self):
        decision = _make_cedar_decision()
        outcome = _make_cedar_outcome()
        evidence = _make_cedar_evidence(strong=True)

        result = classify_causal_link(decision, outcome, evidence)

        if result.label == CausalLabel.EXPLICIT_CAUSAL_LINK:
            assert len(result.rationale) > 0

    def test_confidence_clamped_zero_to_one(self):
        decision = _make_cedar_decision()
        outcome = _make_cedar_outcome()
        evidence = _make_cedar_evidence(strong=True)

        result = classify_causal_link(decision, outcome, evidence)

        assert 0.0 <= result.confidence <= 1.0
