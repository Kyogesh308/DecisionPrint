"""
Outcome extraction from postmortems and incident reports.
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any

from contracts.enums import CausalLabel
from contracts.errors import ExtractionError
from contracts.models import (
    Outcome,
    RecalledMemory,
    RetainResult,
    SourceManifestEntry,
    SourceRef,
)
from intelligence._id_counter import next_outcome_id
from intelligence.llm import LLMUnavailableError, call_llm_json
from intelligence.prompts.extract_outcome_v1 import build_outcome_prompt

logger = logging.getLogger("decisionprint.intelligence.outcomes")


def extract_outcomes(
    source: SourceManifestEntry,
    source_text: str,
    retained: RetainResult,
) -> list[Outcome]:
    """
    Extract Outcome objects from a postmortem or incident report.

    Returns an empty list if no outcomes are found (not an error).
    Raises ExtractionError on LLM failure.
    decision_ids is always [] on return; the causal classifier links them.
    """
    if not source_text.strip():
        logger.warning(
            "extract_outcomes called with empty source_text for %s", source.source_id
        )
        return []

    prompt = build_outcome_prompt(source, source_text, retained.memories)
    cache_key = f"extract_outcomes_{source.source_id}_v1"

    try:
        raw_list = _call_llm_for_outcomes(prompt, cache_key)
    except LLMUnavailableError as exc:
        raise ExtractionError(
            f"LLM unavailable during outcome extraction for {source.source_id}"
        ) from exc

    if not raw_list:
        logger.info("No outcomes extracted from %s", source.source_id)
        return []

    memory_index = {m.memory_id: m for m in retained.memories}
    source_ref = SourceRef(
        source_id=source.source_id,
        document_id=retained.document_id,
    )

    outcomes: list[Outcome] = []
    for i, raw in enumerate(raw_list):
        try:
            outcome = _build_outcome(raw, source, source_ref, memory_index)
            outcomes.append(outcome)
        except (KeyError, TypeError, ValueError) as exc:
            logger.warning(
                "Outcome candidate %d from %s failed assembly: %s",
                i,
                source.source_id,
                exc,
            )

    logger.info("Extracted %d outcome(s) from %s", len(outcomes), source.source_id)
    return outcomes


# --------------------------------------------------------------------------- #
# LLM call                                                                     #
# --------------------------------------------------------------------------- #


def _call_llm_for_outcomes(prompt: str, cache_key: str) -> list[dict[str, Any]]:
    from pydantic import BaseModel

    class _OutcomeEnvelope(BaseModel):
        outcomes: list[dict]

    result = call_llm_json(
        prompt=prompt + '\n\nIMPORTANT: wrap your array as: {"outcomes": [...]}',
        schema=_OutcomeEnvelope,
        cache_key=cache_key,
    )
    return result.outcomes  # type: ignore[attr-defined]


# --------------------------------------------------------------------------- #
# Object assembly                                                               #
# --------------------------------------------------------------------------- #


def _build_outcome(
    raw: dict[str, Any],
    source: SourceManifestEntry,
    source_ref: SourceRef,
    memory_index: dict[str, RecalledMemory],
) -> Outcome:
    statement = str(raw.get("statement") or "").strip()
    if not statement:
        raise ValueError("Outcome statement is empty")

    occurred_at = _parse_occurred_at(raw.get("occurred_at"), source)
    outcome_id = next_outcome_id(source.project_id)
    memory_id = _resolve_memory_id(raw.get("source_memory_id"), memory_index)
    confidence = max(0.0, min(1.0, float(raw.get("confidence") or 0.5)))

    outcome_source_refs = [source_ref]
    if memory_id:
        from contracts.models import SourceRef as SR

        outcome_source_refs.append(
            SR(source_id=source.source_id, document_id=memory_id)
        )

    return Outcome(
        outcome_id=outcome_id,
        project_id=source.project_id,
        occurred_at=occurred_at,
        statement=statement,
        source_refs=outcome_source_refs,
        decision_ids=[],  # ALWAYS empty here; classifier links later
        causal_label=CausalLabel.NONE,  # placeholder; classifier overwrites
        confidence=confidence,
    )


# --------------------------------------------------------------------------- #
# Helpers                                                                       #
# --------------------------------------------------------------------------- #


def _resolve_memory_id(raw_id: Any, memory_index: dict) -> str | None:
    if not raw_id:
        return None
    sid = str(raw_id).strip()
    if sid not in memory_index:
        logger.debug("Hallucinated memory_id '%s' dropped from outcome extraction", sid)
        return None
    return sid


def _parse_occurred_at(raw: Any, source: SourceManifestEntry) -> datetime:
    if raw:
        for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d"):
            try:
                dt = datetime.strptime(str(raw).strip()[:19], fmt)
                return dt.replace(tzinfo=UTC)
            except ValueError:
                continue
    if source.occurred_at:
        return (
            source.occurred_at
            if source.occurred_at.tzinfo
            else source.occurred_at.replace(tzinfo=UTC)
        )
    return datetime.now(tz=UTC)
