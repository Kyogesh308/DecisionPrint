"""
Decision extraction from retained source documents.
LLM output → Pydantic validation → list[Decision].
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any

from pydantic import ValidationError

from contracts.constants import CONSTRAINT_KEYS, LOW_EXTRACTION_CONFIDENCE
from contracts.enums import AssumptionStatus, DecisionStatus
from contracts.errors import ExtractionError, ValidationFailedError
from contracts.models import (
    Alternative,
    Assumption,
    Constraint,
    Decision,
    Reason,
    RecalledMemory,
    RetainResult,
    SourceManifestEntry,
    SourceRef,
)
from intelligence._id_counter import next_decision_id
from intelligence.llm import LLMUnavailableError, call_llm_json
from intelligence.prompts.extract_decision_v1 import build_extraction_prompt

logger = logging.getLogger("decisionprint.intelligence.extraction")

# --------------------------------------------------------------------------- #
# Public entry point                                                            #
# --------------------------------------------------------------------------- #


def extract_decisions(
    source: SourceManifestEntry,
    source_text: str,
    retained: RetainResult,
) -> list[Decision]:
    """
    Extract canonical Decision objects from a retained source document.

    Raises ExtractionError if the LLM returns unrecoverable output after retries.
    Raises ValidationFailedError if all extracted candidates fail Pydantic validation.
    Returns an empty list if the document contains no extractable decisions.
    """
    if not source_text.strip():
        logger.warning(
            "extract_decisions called with empty source_text for %s", source.source_id
        )
        return []

    prompt = build_extraction_prompt(source, source_text, retained.memories)
    cache_key = f"extract_decisions_{source.source_id}_v1"

    try:
        raw_list: list[dict[str, Any]] = _call_llm_for_decisions(prompt, cache_key)
    except LLMUnavailableError as exc:
        raise ExtractionError(
            f"LLM unavailable during decision extraction for {source.source_id}"
        ) from exc

    if not raw_list:
        logger.info("No decisions extracted from %s", source.source_id)
        return []

    memory_index = _build_memory_index(retained.memories)
    decisions: list[Decision] = []
    failures: list[str] = []

    for i, raw in enumerate(raw_list):
        try:
            decision = _build_decision(
                raw=raw,
                source=source,
                retained=retained,
                memory_index=memory_index,
                seq=len(decisions) + 1,  # 1-based, increments only on success
            )
            decisions.append(decision)
        except (ValidationError, KeyError, TypeError, ValueError) as exc:
            msg = f"Candidate {i} from {source.source_id} failed validation: {exc}"
            logger.warning(msg)
            failures.append(msg)

    if not decisions and failures:
        raise ValidationFailedError(
            f"All {len(failures)} decision candidates from {source.source_id} "
            f"failed validation. First failure: {failures[0]}"
        )

    logger.info(
        "Extracted %d decision(s) from %s (%d candidate(s) failed validation)",
        len(decisions),
        source.source_id,
        len(failures),
    )
    return decisions


# --------------------------------------------------------------------------- #
# LLM call                                                                     #
# --------------------------------------------------------------------------- #


def _call_llm_for_decisions(prompt: str, cache_key: str) -> list[dict[str, Any]]:
    """
    Call the LLM and return a raw list of dicts.
    The LLM is instructed to return a JSON array; call_llm_json handles parse + retry.
    We pass a minimal envelope schema here because the full Decision schema is too
    complex to validate at the LLM boundary — Pydantic validation happens in
    _build_decision after we normalise the raw dict.
    """
    # We ask the LLM for a JSON object wrapping the array so call_llm_json
    # can validate against a simple schema. Unwrap immediately.
    from pydantic import BaseModel

    class _Envelope(BaseModel):
        decisions: list[dict]

    result = call_llm_json(
        prompt=prompt + '\n\nIMPORTANT: wrap your array as: {"decisions": [...]}',
        schema=_Envelope,
        cache_key=cache_key,
    )
    return result.decisions  # type: ignore[attr-defined]


# --------------------------------------------------------------------------- #
# Decision assembly                                                             #
# --------------------------------------------------------------------------- #


def _build_decision(
    raw: dict[str, Any],
    source: SourceManifestEntry,
    retained: RetainResult,
    memory_index: dict[str, RecalledMemory],
    seq: int,
) -> Decision:
    """
    Convert one raw LLM dict into a validated Decision.
    All field-level transforms happen here, not in the prompt.
    """
    project_id = source.project_id
    decision_id = next_decision_id(project_id)

    reason_linked_keys: set[str] = set(raw.get("reason_linked_constraint_keys") or [])

    constraints = _parse_constraints(
        raw_constraints=raw.get("constraints") or [],
        reason_linked_keys=reason_linked_keys,
        memory_index=memory_index,
    )
    reasons = _parse_reasons(raw.get("reasons") or [], memory_index)
    alternatives = _parse_alternatives(raw.get("alternatives") or [], memory_index)
    assumptions = _parse_assumptions(raw.get("assumptions") or [], memory_index)

    occurred_at = _parse_occurred_at(raw.get("occurred_at"), source)
    extraction_confidence = _clamp(float(raw.get("extraction_confidence") or 0.0))
    needs_review = extraction_confidence < LOW_EXTRACTION_CONFIDENCE

    source_ref = SourceRef(
        source_id=source.source_id,
        document_id=retained.document_id,
    )

    return Decision(
        id=decision_id,
        project_id=project_id,
        title=str(raw.get("title") or "Untitled Decision")[:120],
        decision_statement=str(raw.get("decision_statement") or ""),
        occurred_at=occurred_at,
        participants=[str(p) for p in (raw.get("participants") or [])],
        context_summary=str(raw.get("context_summary") or ""),
        constraints=constraints,
        assumptions=assumptions,
        alternatives=alternatives,
        selected_option=str(raw.get("selected_option") or ""),
        reasons=reasons,
        technologies=[str(t) for t in (raw.get("technologies") or [])],
        source_refs=[source_ref],
        extraction_confidence=extraction_confidence,
        outcome_refs=[],
        status=DecisionStatus.active,
        superseded_by=None,
        related_decisions=[],
        needs_review=needs_review,
    )


# --------------------------------------------------------------------------- #
# Field parsers                                                                 #
# --------------------------------------------------------------------------- #


def _parse_constraints(
    raw_constraints: list[dict],
    reason_linked_keys: set[str],
    memory_index: dict[str, RecalledMemory],
) -> list[Constraint]:
    """
    Parse raw constraint dicts. Sets is_reason_linked based on the LLM's
    reason_linked_constraint_keys field. Validates key is known or logs a warning.
    """
    result = []
    for rc in raw_constraints:
        key = str(rc.get("key") or "").strip()
        if not key:
            continue

        if key not in CONSTRAINT_KEYS:
            logger.warning("Unknown constraint key '%s' — retained as-is", key)

        memory_id = _resolve_memory_id(rc.get("source_memory_id"), memory_index)
        is_reason_linked = key in reason_linked_keys

        result.append(
            Constraint(
                key=key,
                value=rc.get("value"),  # str | int | float | bool | None
                unit=rc.get("unit") or None,
                normalized_value=None,  # Phase 1 normalize_constraints handles this
                source_memory_id=memory_id,
                is_reason_linked=is_reason_linked,
            )
        )
    return result


def _parse_reasons(
    raw_reasons: list[dict],
    memory_index: dict[str, RecalledMemory],
) -> list[Reason]:
    result = []
    for rr in raw_reasons:
        statement = str(rr.get("statement") or "").strip()
        if not statement:
            continue
        memory_id = _resolve_memory_id(rr.get("source_memory_id"), memory_index)
        result.append(Reason(statement=statement, source_memory_id=memory_id))
    return result


def _parse_alternatives(
    raw_alternatives: list[dict],
    memory_index: dict[str, RecalledMemory],
) -> list[Alternative]:
    from contracts.enums import AlternativeDisposition

    valid_dispositions = {d.value for d in AlternativeDisposition}

    result = []
    for ra in raw_alternatives:
        option = str(ra.get("option") or "").strip()
        if not option:
            continue
        raw_disp = str(ra.get("disposition") or "deferred").lower()
        if raw_disp not in valid_dispositions:
            logger.warning(
                "Unknown disposition '%s', defaulting to 'deferred'", raw_disp
            )
            raw_disp = "deferred"
        memory_id = _resolve_memory_id(ra.get("source_memory_id"), memory_index)
        result.append(
            Alternative(
                option=option,
                disposition=AlternativeDisposition(raw_disp),
                reason=ra.get("reason") or None,
                source_memory_id=memory_id,
            )
        )
    return result


def _parse_assumptions(
    raw_assumptions: list[dict],
    memory_index: dict[str, RecalledMemory],
) -> list[Assumption]:
    result = []
    for ra in raw_assumptions:
        statement = str(ra.get("statement") or "").strip()
        if not statement:
            continue
        memory_id = _resolve_memory_id(ra.get("source_memory_id"), memory_index)
        result.append(
            Assumption(
                statement=statement,
                status=AssumptionStatus.active,
                source_memory_id=memory_id,
            )
        )
    return result


# --------------------------------------------------------------------------- #
# Helpers                                                                       #
# --------------------------------------------------------------------------- #


def _build_memory_index(memories: list[RecalledMemory]) -> dict[str, RecalledMemory]:
    """Map memory_id → RecalledMemory for O(1) validation lookups."""
    return {m.memory_id: m for m in memories}


def _resolve_memory_id(
    raw_id: Any,
    memory_index: dict[str, RecalledMemory],
) -> str | None:
    """
    Return the memory_id string if it exists in the index, else None.
    The LLM occasionally hallucinates IDs; this guards against that.
    """
    if not raw_id:
        return None
    sid = str(raw_id).strip()
    if sid not in memory_index:
        logger.debug(
            "LLM produced memory_id '%s' not found in retained memories — dropping", sid
        )
        return None
    return sid


def _parse_occurred_at(raw: Any, source: SourceManifestEntry) -> datetime:
    """
    Parse the LLM's occurred_at string. Falls back to source.occurred_at,
    then to UTC now. Always returns a timezone-aware datetime.
    """
    if raw:
        for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d"):
            try:
                dt = datetime.strptime(str(raw).strip()[:19], fmt)
                return dt.replace(tzinfo=UTC)
            except ValueError:
                continue
        logger.warning(
            "Could not parse occurred_at '%s', falling back to source date", raw
        )

    if source.occurred_at:
        return (
            source.occurred_at
            if source.occurred_at.tzinfo
            else source.occurred_at.replace(tzinfo=UTC)
        )

    logger.warning("No occurred_at for %s — using UTC now", source.source_id)
    return datetime.now(tz=UTC)


def _clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, value))
