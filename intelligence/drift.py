"""
intelligence/drift.py

Drift engine: normalize constraints, compare historical vs current, score drift.
"""

from __future__ import annotations

import logging
from copy import deepcopy

from contracts.enums import ConstraintComparison, DriftLevel
from contracts.models import (
    Constraint,
    ConstraintDelta,
    ConstraintDeltaItem,
    CurrentProjectContext,
    Decision,
    DriftResult,
)
from intelligence._normalizers import KNOWN_KEYS, normalize_value
from intelligence._weights import (
    DRIFT_THRESHOLDS,
    NON_REASON_LINKED_WEIGHT,
    REASON_LINKED_WEIGHT,
    RECONSIDERATION_MIN_CONFIDENCE,
    RECONSIDERATION_MIN_SCORE,
)

logger = logging.getLogger("decisionprint.intelligence.drift")


def normalize_constraints(
    constraints: list[Constraint],
    *,
    use_llm_for_semantics: bool = False,
) -> list[Constraint]:
    result: list[Constraint] = []
    for c in constraints:
        normalized = deepcopy(c)
        canonical = normalize_value(c.key, c.value)

        if canonical is not None:
            normalized.normalized_value = canonical
        elif use_llm_for_semantics and c.key in KNOWN_KEYS:
            canonical = _normalize_via_llm(c.key, c.value)
            normalized.normalized_value = canonical
        else:
            normalized.normalized_value = None
            if c.key in KNOWN_KEYS:
                logger.warning(
                    "normalize_constraints: could not normalize key=%r value=%r",
                    c.key,
                    c.value,
                )

        result.append(normalized)
    return result


def _normalize_via_llm(key: str, raw_value: object) -> object | None:
    from intelligence.llm import call_llm_text

    cache_key = f"normalize_semantic_v1:{key}:{raw_value}"
    prompt = (
        f"You are normalizing a constraint value for the key '{key}'.\n"
        f"Raw value: {raw_value!r}\n"
        f"Return ONLY the normalized value as a raw JSON scalar "
        f"(string, integer, or boolean). No explanation, no quotes around the JSON."
    )
    try:
        raw = call_llm_text(prompt, cache_key=cache_key).strip()
        import json

        return json.loads(raw)
    except Exception as exc:
        logger.warning(
            "LLM normalization failed for key=%r value=%r: %s", key, raw_value, exc
        )
        return None


def compare_constraints(
    decision: Decision,
    current: CurrentProjectContext,
) -> ConstraintDelta:
    historical_by_key: dict[str, Constraint] = {c.key: c for c in decision.constraints}
    current_by_key: dict[str, Constraint] = {c.key: c for c in current.constraints}
    items: list[ConstraintDeltaItem] = []

    for key, hist_c in historical_by_key.items():
        is_reason_linked = hist_c.is_reason_linked
        weight = REASON_LINKED_WEIGHT if is_reason_linked else NON_REASON_LINKED_WEIGHT

        if key not in current_by_key:
            items.append(
                ConstraintDeltaItem(
                    key=key,
                    historical_value=_effective_value(hist_c),
                    current_value=None,
                    comparison=ConstraintComparison.UNKNOWN,
                    is_reason_linked=is_reason_linked,
                    weight=weight,
                    note="Constraint not present in current project context.",
                )
            )
            continue

        curr_c = current_by_key[key]
        hist_val = _effective_value(hist_c)
        curr_val = _effective_value(curr_c)

        comparison, note = _classify_pair(key, hist_val, curr_val)
        items.append(
            ConstraintDeltaItem(
                key=key,
                historical_value=hist_val,
                current_value=curr_val,
                comparison=comparison,
                is_reason_linked=is_reason_linked,
                weight=weight,
                note=note,
            )
        )

    for key, curr_c in current_by_key.items():
        if key not in historical_by_key:
            items.append(
                ConstraintDeltaItem(
                    key=key,
                    historical_value=None,
                    current_value=_effective_value(curr_c),
                    comparison=ConstraintComparison.NEWLY_PRESENT,
                    is_reason_linked=False,
                    weight=NON_REASON_LINKED_WEIGHT,
                    note="Constraint not present in historical decision.",
                )
            )

    return ConstraintDelta(
        decision_id=decision.id,
        project_id=current.project_id,
        items=items,
    )


def _effective_value(c: Constraint) -> object:
    if c.normalized_value is not None:
        return c.normalized_value
    return c.value


def _classify_pair(
    key: str, hist_val: object, curr_val: object
) -> tuple[ConstraintComparison, str | None]:
    if hist_val is None and curr_val is None:
        return ConstraintComparison.INCOMPARABLE, "Both values are null."
    if hist_val is None or curr_val is None:
        return ConstraintComparison.INCOMPARABLE, "One value is null; cannot compare."
    if type(hist_val) is not type(curr_val):
        return (
            ConstraintComparison.INCOMPARABLE,
            f"Type mismatch: historical={type(hist_val).__name__}, current={type(curr_val).__name__}.",
        )
    if isinstance(hist_val, (int, float)) and isinstance(curr_val, (int, float)):
        if hist_val == curr_val:
            return ConstraintComparison.SAME, None
        return ConstraintComparison.CHANGED, f"{hist_val} → {curr_val}"
    if isinstance(hist_val, bool):
        if hist_val == curr_val:
            return ConstraintComparison.SAME, None
        return ConstraintComparison.CHANGED, f"{hist_val} → {curr_val}"
    if isinstance(hist_val, str):
        if hist_val.lower() == curr_val.lower():  # type: ignore[union-attr]
            return ConstraintComparison.SAME, None
        return ConstraintComparison.CHANGED, f'"{hist_val}" → "{curr_val}"'
    if hist_val == curr_val:
        return ConstraintComparison.SAME, None
    return ConstraintComparison.CHANGED, f"{hist_val!r} → {curr_val!r}"


def score_drift(delta: ConstraintDelta) -> DriftResult:
    reason_linked_items = [i for i in delta.items if i.is_reason_linked]
    if not reason_linked_items:
        logger.debug(
            "score_drift: no reason-linked constraints in delta — returning none"
        )
        return DriftResult(
            decision_id=delta.decision_id,
            score=0.0,
            level=DriftLevel.NONE,
            reconsideration_warranted=False,
            drift_confidence=0.0,
            delta=delta,
        )

    changed_weight = sum(
        i.weight
        for i in reason_linked_items
        if i.comparison == ConstraintComparison.CHANGED
    )
    known_weight = sum(
        i.weight
        for i in reason_linked_items
        if i.comparison in {ConstraintComparison.SAME, ConstraintComparison.CHANGED}
    )

    comparable_count = sum(
        1
        for i in reason_linked_items
        if i.comparison in {ConstraintComparison.SAME, ConstraintComparison.CHANGED}
    )
    drift_confidence = comparable_count / len(reason_linked_items)

    if known_weight == 0.0:
        drift_score = 0.0
    else:
        drift_score = changed_weight / known_weight

    drift_score = max(0.0, min(1.0, drift_score))
    level = _score_to_level(drift_score)

    reconsideration_warranted = (
        drift_score >= RECONSIDERATION_MIN_SCORE
        and drift_confidence >= RECONSIDERATION_MIN_CONFIDENCE
    )

    logger.debug(
        "score_drift: decision=%s score=%.3f level=%s confidence=%.3f warranted=%s",
        delta.decision_id,
        drift_score,
        level.value,
        drift_confidence,
        reconsideration_warranted,
    )

    return DriftResult(
        decision_id=delta.decision_id,
        score=round(drift_score, 4),
        level=level,
        reconsideration_warranted=reconsideration_warranted,
        drift_confidence=round(drift_confidence, 4),
        delta=delta,
    )


def _score_to_level(score: float) -> DriftLevel:
    for label, low, high in DRIFT_THRESHOLDS:
        if low <= score < high:
            return DriftLevel(label)
    return DriftLevel.HIGH
