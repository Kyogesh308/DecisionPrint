"""Tests for extract_decisions — Phase 3."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from contracts.enums import DecisionStatus, MemoryKind
from contracts.errors import ExtractionError, ValidationFailedError
from contracts.models import RecalledMemory, RetainResult, SourceManifestEntry
from intelligence import extract_decisions
from intelligence._id_counter import reset_counters_for_testing

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture(autouse=True)
def reset_ids():
    """Ensure ID counters are clean for each test."""
    reset_counters_for_testing()
    yield
    reset_counters_for_testing()


def _load_source() -> SourceManifestEntry:
    return SourceManifestEntry(
        **json.loads((FIXTURES / "source_alpha_kafka.json").read_text(encoding="utf-8"))
    )


def _make_retained(memory_ids: list[str] | None = None) -> RetainResult:
    ids = memory_ids or ["mem-001", "mem-002", "mem-003"]
    memories = [
        RecalledMemory(
            memory_id=mid,
            kind=MemoryKind.experience,
            text=f"Retained fact {mid}",
            tags=[],
            entities=[],
            source_refs=[],
            relevance=1.0,
        )
        for mid in ids
    ]
    return RetainResult(
        source_id="SRC-ALPHA-001",
        document_id="doc-alpha-001",
        memory_ids=ids,
        memories=memories,
    )


class TestExtractDecisionsAlphaKafka:
    """
    Core extraction test: Alpha ADR must produce a Decision with the exact
    constraint profile required by the Phase 3 exit criteria.
    """

    def test_returns_list_with_one_decision(self):
        source = _load_source()
        text = (FIXTURES / "text_alpha_kafka_adr.txt").read_text(encoding="utf-8")
        retained = _make_retained()

        decisions = extract_decisions(source, text, retained)

        assert isinstance(decisions, list)
        assert len(decisions) == 1

    def test_decision_id_format(self):
        source = _load_source()
        text = (FIXTURES / "text_alpha_kafka_adr.txt").read_text(encoding="utf-8")
        retained = _make_retained()

        decisions = extract_decisions(source, text, retained)

        assert decisions[0].id == "DEC-ALPHA-001"

    def test_decision_project_id(self):
        source = _load_source()
        text = (FIXTURES / "text_alpha_kafka_adr.txt").read_text(encoding="utf-8")
        retained = _make_retained()

        decisions = extract_decisions(source, text, retained)

        assert decisions[0].project_id == "alpha"

    def test_constraint_consumer_count_extracted(self):
        """Phase 3 exit criterion: consumer_count=2 must be present."""
        source = _load_source()
        text = (FIXTURES / "text_alpha_kafka_adr.txt").read_text(encoding="utf-8")
        retained = _make_retained()

        decisions = extract_decisions(source, text, retained)
        constraint_map = {c.key: c for c in decisions[0].constraints}

        assert "consumer_count" in constraint_map
        assert "2" in str(constraint_map["consumer_count"].value)

    def test_constraint_replay_required_false(self):
        """Phase 3 exit criterion: replay_required=False must be present."""
        source = _load_source()
        text = (FIXTURES / "text_alpha_kafka_adr.txt").read_text(encoding="utf-8")
        retained = _make_retained()

        decisions = extract_decisions(source, text, retained)
        constraint_map = {c.key: c for c in decisions[0].constraints}

        assert "replay_required" in constraint_map
        raw_val = str(constraint_map["replay_required"].value).lower()
        assert "no" in raw_val or "false" in raw_val or "0" in raw_val

    def test_constraint_traffic_volume_moderate(self):
        """Phase 3 exit criterion: traffic_volume=moderate must be present."""
        source = _load_source()
        text = (FIXTURES / "text_alpha_kafka_adr.txt").read_text(encoding="utf-8")
        retained = _make_retained()

        decisions = extract_decisions(source, text, retained)
        constraint_map = {c.key: c for c in decisions[0].constraints}

        assert "traffic_volume" in constraint_map
        assert "moderate" in str(constraint_map["traffic_volume"].value).lower()

    def test_constraint_ops_capacity_small(self):
        """Phase 3 exit criterion: ops_capacity=small must be present."""
        source = _load_source()
        text = (FIXTURES / "text_alpha_kafka_adr.txt").read_text(encoding="utf-8")
        retained = _make_retained()

        decisions = extract_decisions(source, text, retained)
        constraint_map = {c.key: c for c in decisions[0].constraints}

        assert "ops_capacity" in constraint_map
        assert "small" in str(constraint_map["ops_capacity"].value).lower()

    def test_reason_linked_constraints_are_flagged(self):
        """Constraints the reasons depend on must have is_reason_linked=True."""
        source = _load_source()
        text = (FIXTURES / "text_alpha_kafka_adr.txt").read_text(encoding="utf-8")
        retained = _make_retained()

        decisions = extract_decisions(source, text, retained)
        constraint_map = {c.key: c for c in decisions[0].constraints}

        for key in (
            "consumer_count",
            "replay_required",
            "traffic_volume",
            "ops_capacity",
        ):
            assert constraint_map[key].is_reason_linked is True, (
                f"Expected is_reason_linked=True for '{key}'"
            )

    def test_reasons_are_present(self):
        source = _load_source()
        text = (FIXTURES / "text_alpha_kafka_adr.txt").read_text(encoding="utf-8")
        retained = _make_retained()

        decisions = extract_decisions(source, text, retained)

        assert len(decisions[0].reasons) > 0

    def test_kafka_alternative_marked_rejected(self):
        source = _load_source()
        text = (FIXTURES / "text_alpha_kafka_adr.txt").read_text(encoding="utf-8")
        retained = _make_retained()

        decisions = extract_decisions(source, text, retained)
        alternatives = {a.option.lower(): a for a in decisions[0].alternatives}

        kafka_alt = next((a for k, a in alternatives.items() if "kafka" in k), None)
        assert kafka_alt is not None, "Kafka must appear as a rejected alternative"
        assert getattr(kafka_alt.disposition, "value", kafka_alt.disposition) == "rejected"

    def test_source_ref_populated(self):
        source = _load_source()
        text = (FIXTURES / "text_alpha_kafka_adr.txt").read_text(encoding="utf-8")
        retained = _make_retained()

        decisions = extract_decisions(source, text, retained)

        assert len(decisions[0].source_refs) == 1
        assert decisions[0].source_refs[0].source_id == "SRC-ALPHA-001"
        assert decisions[0].source_refs[0].document_id == "doc-alpha-001"

    def test_status_is_active(self):
        source = _load_source()
        text = (FIXTURES / "text_alpha_kafka_adr.txt").read_text(encoding="utf-8")
        retained = _make_retained()

        decisions = extract_decisions(source, text, retained)

        assert decisions[0].status == "active"


class TestExtractDecisionsEdgeCases:
    def test_returns_empty_list_for_no_decision_text(self):
        source = _load_source()
        source.source_id = "SRC-EMPTY-001"
        text = (FIXTURES / "text_logistics_email.txt").read_text(encoding="utf-8")
        retained = _make_retained()

        decisions = extract_decisions(source, text, retained)

        assert decisions == []

    def test_returns_empty_list_for_blank_source_text(self):
        source = _load_source()
        retained = _make_retained()

        decisions = extract_decisions(source, "   ", retained)

        assert decisions == []

    def test_hallucinated_memory_ids_are_dropped(self):
        """LLM returns a memory_id not in retained.memories — must be None, not error."""
        source = _load_source()
        text = (FIXTURES / "text_alpha_kafka_adr.txt").read_text(encoding="utf-8")
        retained = _make_retained(memory_ids=["real-mem-001"])

        # The LLM prompt includes only real-mem-001, so hallucinated IDs should
        # be dropped. This is tested by checking no constraint has a non-existent ID.
        decisions = extract_decisions(source, text, retained)

        for d in decisions:
            for c in d.constraints:
                assert c.source_memory_id in (None, "real-mem-001")

    def test_low_confidence_sets_needs_review(self):
        """Decisions with extraction_confidence < 0.60 must have needs_review=True."""
        # Patch call_llm_json to return a low-confidence decision
        low_conf_raw = {
            "decisions": [
                {
                    "title": "Uncertain decision",
                    "decision_statement": "We might use something.",
                    "occurred_at": None,
                    "participants": [],
                    "context_summary": "unclear",
                    "selected_option": "unknown",
                    "technologies": [],
                    "extraction_confidence": 0.45,
                    "constraints": [],
                    "reasons": [],
                    "alternatives": [],
                    "assumptions": [],
                    "reason_linked_constraint_keys": [],
                }
            ]
        }
        source = _load_source()
        retained = _make_retained()

        with patch("intelligence.extraction.call_llm_json") as mock_llm:
            from pydantic import BaseModel

            class _Env(BaseModel):
                decisions: list[dict]

            mock_llm.return_value = _Env(decisions=low_conf_raw["decisions"])
            decisions = extract_decisions(source, "some text", retained)

        assert decisions[0].needs_review is True
        assert decisions[0].extraction_confidence == pytest.approx(0.45)

    def test_high_confidence_does_not_set_needs_review(self):
        high_conf_raw = {
            "decisions": [
                {
                    "title": "Clear decision",
                    "decision_statement": "We will use Redis Streams.",
                    "occurred_at": "2025-03-14",
                    "participants": ["Alice"],
                    "context_summary": "clear context",
                    "selected_option": "Redis Streams",
                    "technologies": ["Redis"],
                    "extraction_confidence": 0.88,
                    "constraints": [],
                    "reasons": [
                        {"statement": "Low consumer count.", "source_memory_id": None}
                    ],
                    "alternatives": [],
                    "assumptions": [],
                    "reason_linked_constraint_keys": [],
                }
            ]
        }
        source = _load_source()
        retained = _make_retained()

        with patch("intelligence.extraction.call_llm_json") as mock_llm:
            from pydantic import BaseModel

            class _Env(BaseModel):
                decisions: list[dict]

            mock_llm.return_value = _Env(decisions=high_conf_raw["decisions"])
            decisions = extract_decisions(source, "some text", retained)

        assert decisions[0].needs_review is False

    def test_sequential_ids_across_calls(self):
        """Two calls for the same project must produce DEC-ALPHA-001, DEC-ALPHA-002."""
        source = _load_source()
        text = (FIXTURES / "text_alpha_kafka_adr.txt").read_text(encoding="utf-8")
        retained = _make_retained()

        d1 = extract_decisions(source, text, retained)
        d2 = extract_decisions(source, text, retained)

        assert d1[0].id == "DEC-ALPHA-001"
        assert d2[0].id == "DEC-ALPHA-002"

    def test_llm_unavailable_raises_extraction_error(self):
        from intelligence.llm import LLMUnavailableError

        source = _load_source()
        retained = _make_retained()

        with (
            patch(
                "intelligence.extraction.call_llm_json",
                side_effect=LLMUnavailableError("timeout"),
            ),
            pytest.raises(ExtractionError),
        ):
            extract_decisions(source, "text", retained)

    def test_all_candidates_invalid_raises_validation_failed(self):
        """If every LLM candidate fails Pydantic validation, raise ValidationFailedError."""
        source = _load_source()
        source.source_id = "SRC-INVALID-002"
        retained = _make_retained()

        with (
            patch(
                "intelligence.extraction._call_llm_for_decisions",
                return_value=[{"extraction_confidence": "unparseable"}],
            ),
            pytest.raises(ValidationFailedError),
        ):
            extract_decisions(source, "some text", retained)
