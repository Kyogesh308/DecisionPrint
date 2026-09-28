"""
Current project context extraction from meeting transcripts.
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime

from pydantic import ValidationError

from contracts.constants import CONSTRAINT_KEYS
from contracts.errors import ExtractionError, ValidationFailedError
from contracts.models import (
    Constraint,
    CurrentProjectContext,
    RecalledMemory,
    RetainResult,
    SourceManifestEntry,
    SourceRef,
)
from intelligence.llm import LLMUnavailableError, call_llm_json
from intelligence.prompts.extract_context_v1 import build_context_prompt

logger = logging.getLogger("decisionprint.intelligence.context")


def extract_current_context(
    source: SourceManifestEntry,
    source_text: str,
    retained: RetainResult,
) -> CurrentProjectContext:
    """
    Extract the current project's constraint context from a meeting transcript.

    Raises ExtractionError if the LLM fails after retries.
    Raises ValidationFailedError if the LLM output cannot be validated.
    Never returns None; returns a context with empty constraints if none found.
    """
    if not source_text.strip():
        logger.warning(
            "extract_current_context called with empty source_text for %s",
            source.source_id,
        )
        return _empty_context(source, retained)

    prompt = build_context_prompt(source, source_text, retained.memories)
    cache_key = f"extract_context_{source.source_id}_v1"

    try:
        raw = _call_llm_for_context(prompt, cache_key)
    except LLMUnavailableError as exc:
        raise ExtractionError(
            f"LLM unavailable during context extraction for {source.source_id}"
        ) from exc

    memory_index = {m.memory_id: m for m in retained.memories}

    try:
        return _build_context(raw, source, retained, memory_index)
    except (ValidationError, KeyError, TypeError, ValueError) as exc:
        raise ValidationFailedError(
            f"Context extraction output failed validation for {source.source_id}: {exc}"
        ) from exc


# --------------------------------------------------------------------------- #
# LLM call                                                                     #
# --------------------------------------------------------------------------- #


def _call_llm_for_context(prompt: str, cache_key: str) -> dict:
    """
    Call the LLM and return a raw dict.
    Unlike extraction.py, we get a single object, not a list,
    so no envelope wrapping is needed.
    """
    from pydantic import BaseModel

    class _ContextEnvelope(BaseModel):
        project_id: str
        summary: str
        constraints: list[dict]
        extraction_confidence: float

    result = call_llm_json(prompt=prompt, schema=_ContextEnvelope, cache_key=cache_key)
    return result.model_dump()


# --------------------------------------------------------------------------- #
# Object assembly                                                               #
# --------------------------------------------------------------------------- #


def _build_context(
    raw: dict,
    source: SourceManifestEntry,
    retained: RetainResult,
    memory_index: dict[str, RecalledMemory],
) -> CurrentProjectContext:
    constraints = _parse_constraints(raw.get("constraints") or [], memory_index)
    source_ref = SourceRef(
        source_id=source.source_id,
        document_id=retained.document_id,
    )

    return CurrentProjectContext(
        project_id=source.project_id,  # always trust source, not LLM
        summary=str(raw.get("summary") or ""),
        constraints=constraints,
        source_refs=[source_ref],
        updated_at=source.occurred_at or datetime.now(tz=UTC),
    )


def _parse_constraints(
    raw_constraints: list[dict],
    memory_index: dict[str, RecalledMemory],
) -> list[Constraint]:
    result = []
    for rc in raw_constraints:
        key = str(rc.get("key") or "").strip()
        if not key:
            continue
        if key not in CONSTRAINT_KEYS:
            logger.warning(
                "extract_current_context: unknown constraint key '%s' — dropped", key
            )
            continue  # STRICTER than extraction: unknown keys are dropped here, not retained

        memory_id = _resolve_memory_id(rc.get("source_memory_id"), memory_index)
        result.append(
            Constraint(
                key=key,
                value=rc.get("value"),
                unit=rc.get("unit") or None,
                normalized_value=None,  # Phase 1 normalize_constraints handles this
                source_memory_id=memory_id,
                is_reason_linked=False,  # always False here per contract
            )
        )
    return result


def _resolve_memory_id(raw_id, memory_index: dict) -> str | None:
    if not raw_id:
        return None
    sid = str(raw_id).strip()
    if sid not in memory_index:
        logger.debug("Hallucinated memory_id '%s' dropped from context extraction", sid)
        return None
    return sid


def _empty_context(
    source: SourceManifestEntry, retained: RetainResult
) -> CurrentProjectContext:
    return CurrentProjectContext(
        project_id=source.project_id,
        summary="",
        constraints=[],
        source_refs=[
            SourceRef(source_id=source.source_id, document_id=retained.document_id)
        ],
        updated_at=source.occurred_at or datetime.now(tz=UTC),
    )
