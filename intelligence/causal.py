"""
Causal link classification between decisions and outcomes.

HARD RULE (from PRD and B.9):
If the LLM cannot cite evidence_ids drawn from the provided evidence list,
the label MUST be CausalLabel.NONE.
This rule is enforced at the Python layer, not in the prompt.
The LLM cannot override it.
"""

from __future__ import annotations

import logging
from typing import Any

from contracts.enums import CausalLabel
from contracts.errors import LLMUnavailableError
from contracts.models import CausalLink, Decision, Outcome, RecalledMemory
from intelligence.llm import call_llm_json
from intelligence.prompts.classify_causal_v1 import build_causal_prompt

logger = logging.getLogger("decisionprint.intelligence.causal")

# Minimum evidence required per label — enforced by Python, not the prompt
_MIN_EVIDENCE_IDS: dict[str, int] = {
    "possible_causal_link": 1,
    "strong_evidence": 2,
    "explicit_causal_link": 1,
    "none": 0,
}


def classify_causal_link(
    decision: Decision,
    outcome: Outcome,
    evidence: list[RecalledMemory],
) -> CausalLink:
    """
    Classify the causal relationship between a decision and an outcome.

    Hard rule: if no evidence_ids can be cited from the provided evidence list,
    the label is CausalLabel.NONE regardless of LLM output.
    Always returns a CausalLink; never raises — returns NONE on any failure.
    """
    if not evidence:
        logger.info(
            "classify_causal_link: no evidence provided for %s → %s; returning none",
            decision.id,
            outcome.outcome_id,
        )
        return _none_link(decision.id, outcome.outcome_id, "No evidence provided.")

    valid_memory_ids = {m.memory_id for m in evidence}
    prompt = build_causal_prompt(decision, outcome, evidence)
    cache_key = f"classify_causal_{decision.id}_{outcome.outcome_id}_v1"

    try:
        raw = _call_llm_for_classification(prompt, cache_key)
    except (LLMUnavailableError, Exception) as exc:
        logger.warning(
            "classify_causal_link: LLM failed for %s → %s: %s; returning none",
            decision.id,
            outcome.outcome_id,
            exc,
        )
        return _none_link(
            decision.id, outcome.outcome_id, "Classification unavailable."
        )

    return _apply_evidence_guard(raw, decision.id, outcome.outcome_id, valid_memory_ids)


# --------------------------------------------------------------------------- #
# LLM call                                                                     #
# --------------------------------------------------------------------------- #


def _call_llm_for_classification(prompt: str, cache_key: str) -> dict[str, Any]:
    from pydantic import BaseModel

    class _ClassificationResult(BaseModel):
        label: str
        rationale: str
        evidence_ids: list[str]
        confidence: float

    result = call_llm_json(
        prompt=prompt, schema=_ClassificationResult, cache_key=cache_key
    )
    return result.model_dump()


# --------------------------------------------------------------------------- #
# Evidence guard — THE critical function                                        #
# --------------------------------------------------------------------------- #


def _apply_evidence_guard(
    raw: dict[str, Any],
    decision_id: str,
    outcome_id: str,
    valid_memory_ids: set[str],
) -> CausalLink:
    """
    Enforce the hard rule: if the LLM's claimed evidence_ids don't exist
    in the provided evidence list, downgrade the label.

    This function is the gatekeeper. It runs after every LLM call
    and cannot be bypassed.
    """
    raw_label = str(raw.get("label") or "none").lower().strip()
    raw_evidence_ids: list[str] = raw.get("evidence_ids") or []
    rationale = str(raw.get("rationale") or "")
    confidence = max(0.0, min(1.0, float(raw.get("confidence") or 0.0)))

    # Filter to only IDs that actually exist in the evidence list
    verified_ids = [eid for eid in raw_evidence_ids if eid in valid_memory_ids]

    # Log any hallucinated IDs
    hallucinated = set(raw_evidence_ids) - valid_memory_ids
    if hallucinated:
        logger.warning(
            "classify_causal_link: LLM cited non-existent evidence IDs %s for %s → %s — dropped",
            hallucinated,
            decision_id,
            outcome_id,
        )

    # Validate the label is a known value
    valid_labels = {label.value for label in CausalLabel}
    if raw_label not in valid_labels:
        logger.warning(
            "classify_causal_link: unknown label '%s' for %s → %s — downgrading to none",
            raw_label,
            decision_id,
            outcome_id,
        )
        raw_label = "none"

    # HARD RULE: enforce minimum evidence counts per label
    min_required = _MIN_EVIDENCE_IDS.get(raw_label, 1)
    if len(verified_ids) < min_required:
        logger.info(
            "classify_causal_link: label '%s' requires %d evidence_id(s), "
            "only %d verified for %s → %s — downgrading to none",
            raw_label,
            min_required,
            len(verified_ids),
            decision_id,
            outcome_id,
        )
        return _none_link(
            decision_id,
            outcome_id,
            f"Downgraded from '{raw_label}': insufficient verified evidence. Original rationale: {rationale}",
        )

    return CausalLink(
        decision_id=decision_id,
        outcome_id=outcome_id,
        label=CausalLabel(raw_label),
        rationale=rationale,
        evidence_ids=verified_ids,
        confidence=confidence,
    )


# --------------------------------------------------------------------------- #
# Helpers                                                                       #
# --------------------------------------------------------------------------- #


def _none_link(decision_id: str, outcome_id: str, rationale: str) -> CausalLink:
    """Return a CausalLink with label=none. The safe default."""
    return CausalLink(
        decision_id=decision_id,
        outcome_id=outcome_id,
        label=CausalLabel.NONE,
        rationale=rationale,
        evidence_ids=[],
        confidence=0.0,
    )
