"""
intelligence/brief.py
"""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from typing import Any

from contracts.enums import EpistemicLabel
from contracts.errors import MemoryUnavailableError
from contracts.models import (
    BriefClaim,
    ConfidenceBreakdown,
    Constraint,
    ConstraintDelta,
    CurrentProjectContext,
    Decision,
    DecisionBrief,
    DriftResult,
    RecallBundle,
    ReflectResult,
    Scope,
    SourceRef,
)
from contracts.types import ReflectFn
from intelligence._comparator import (
    build_comparator_text,
    build_multi_decision_comparator,
)
from intelligence.drift import compare_constraints, normalize_constraints, score_drift
from intelligence.prompts.brief_v1 import (
    build_fallback_prompt,
)
from intelligence.prompts.brief_v1 import (
    cache_key as brief_cache_key,
)

logger = logging.getLogger("decisionprint.intelligence.brief")


def build_decision_brief(
    *,
    query_id: str,
    query: str,
    scope: Scope,
    recall: RecallBundle,
    decisions: list[Decision],
    current: CurrentProjectContext | None,
    reflect_fn: ReflectFn,
) -> DecisionBrief:
    project_id = (
        current.project_id
        if current
        else (decisions[0].project_id if decisions else "unknown")
    )

    try:
        return _build_brief(
            query_id=query_id,
            query=query,
            scope=scope,
            recall=recall,
            decisions=decisions,
            current=current,
            reflect_fn=reflect_fn,
            project_id=project_id,
        )
    except Exception as exc:
        logger.error(
            "build_decision_brief: unexpected error for query_id=%s: %s",
            query_id,
            exc,
            exc_info=True,
        )
        return _minimal_safe_brief(
            query_id=query_id,
            query=query,
            project_id=project_id,
            error_message=str(exc),
        )


def _build_brief(
    *,
    query_id: str,
    query: str,
    scope: Scope,
    recall: RecallBundle,
    decisions: list[Decision],
    current: CurrentProjectContext | None,
    reflect_fn: ReflectFn,
    project_id: str,
) -> DecisionBrief:

    drift_results, constraint_deltas, norm_historical, norm_current = _run_drift_engine(
        decisions=decisions,
        current=current,
    )

    comparator_text = _build_comparator(
        decisions=decisions,
        drift_results=drift_results,
        query=query,
        current=current,
    )

    memory_ids = [m.memory_id for m in recall.memories] if recall else []
    source_ids = _collect_source_ids(recall, decisions)

    reflect_result, used_fallback = _call_reflect(
        reflect_fn=reflect_fn,
        query=query,
        scope=scope,
        comparator_text=comparator_text,
        query_id=query_id,
        memory_ids=memory_ids,
        source_ids=source_ids,
    )

    parsed = _parse_reflect_result(
        reflect_result=reflect_result,
        recall=recall,
        decisions=decisions,
        used_fallback=used_fallback,
    )

    historical_decisions = _filter_cited(
        parsed.get("historical_decisions", []), "historical_decisions"
    )
    observations = _filter_cited(parsed.get("observations", []), "observations")
    inferences = _filter_cited(parsed.get("inferences", []), "inferences")
    answer_summary = parsed.get("answer_summary", comparator_text[:500])
    recommendation = _get_recommendation(parsed, drift_results)

    best_drift = _best_drift(drift_results)
    confidence = _build_confidence(
        decisions=decisions,
        recall=recall,
        drift_results=drift_results,
    )
    all_sources = _collect_all_sources(recall, decisions, reflect_result)

    return DecisionBrief(
        query_id=query_id,
        query=query,
        project_id=project_id,
        answer_summary=answer_summary,
        historical_decisions=historical_decisions,
        historical_constraints=norm_historical,
        current_constraints=norm_current,
        constraint_differences=constraint_deltas,
        observations=observations,
        inferences=inferences,
        drift=best_drift,
        reconsideration_warranted=(
            any(dr.reconsideration_warranted for dr in drift_results)
            if drift_results
            else False
        ),
        recommendation=recommendation,
        confidence=confidence,
        sources=all_sources,
        generated_at=datetime.now(UTC).isoformat(),
    )


def _run_drift_engine(
    *,
    decisions: list[Decision],
    current: CurrentProjectContext | None,
) -> tuple[
    list[DriftResult], list[ConstraintDelta], list[Constraint], list[Constraint]
]:
    if not decisions:
        return [], [], [], []

    norm_current: list[Constraint] = []
    if current is not None:
        norm_current = normalize_constraints(current.constraints)
        current_normalized = CurrentProjectContext(
            project_id=current.project_id,
            summary=current.summary,
            constraints=norm_current,
            source_refs=current.source_refs,
            updated_at=current.updated_at,
        )
    else:
        current_normalized = None

    drift_results: list[DriftResult] = []
    constraint_deltas: list[ConstraintDelta] = []
    norm_historical: list[Constraint] = []

    for decision in decisions:
        norm_hist = normalize_constraints(decision.constraints)
        norm_historical.extend(norm_hist)

        if current_normalized is not None:
            norm_decision = Decision.model_validate(
                {
                    **decision.model_dump(),
                    "constraints": [c.model_dump() for c in norm_hist],
                }
            )
            delta = compare_constraints(norm_decision, current_normalized)
            drift_result = score_drift(delta)
        else:
            delta = ConstraintDelta(
                decision_id=decision.id,
                project_id=decision.project_id,
                items=[],
            )
            from contracts.enums import DriftLevel

            drift_result = DriftResult(
                decision_id=decision.id,
                score=0.0,
                level=DriftLevel.NONE,
                reconsideration_warranted=False,
                drift_confidence=0.0,
                delta=delta,
            )

        constraint_deltas.append(delta)
        drift_results.append(drift_result)

    return drift_results, constraint_deltas, norm_historical, norm_current


def _build_comparator(
    *,
    decisions: list[Decision],
    drift_results: list[DriftResult],
    query: str,
    current: CurrentProjectContext | None,
) -> str:
    if not decisions or not drift_results:
        return f"No historical decisions found relevant to: {query}"

    pairs = list(zip(decisions, drift_results))
    if len(pairs) == 1:
        decision, drift_result = pairs[0]
        return build_comparator_text(
            decision=decision,
            drift_result=drift_result,
            query=query,
        )
    return build_multi_decision_comparator(
        decisions_and_drift=pairs,
        query=query,
    )


def _call_reflect(
    *,
    reflect_fn: ReflectFn,
    query: str,
    scope: Scope,
    comparator_text: str,
    query_id: str,
    memory_ids: list[str],
    source_ids: list[str],
) -> tuple[ReflectResult, bool]:
    try:
        result = reflect_fn(query, scope, context=comparator_text)
        logger.debug("reflect_fn succeeded for query_id=%s", query_id)
        return result, False
    except MemoryUnavailableError as exc:
        logger.warning(
            "reflect_fn unavailable for query_id=%s (%s) — using LLM fallback",
            query_id,
            exc,
        )
        return _fallback_reflect(
            query=query,
            comparator_text=comparator_text,
            query_id=query_id,
            memory_ids=memory_ids,
            source_ids=source_ids,
        ), True


def _fallback_reflect(
    *,
    query: str,
    comparator_text: str,
    query_id: str,
    memory_ids: list[str],
    source_ids: list[str],
) -> ReflectResult:
    from intelligence.llm import call_llm_text

    prompt = build_fallback_prompt(
        query=query,
        comparator_text=comparator_text,
        memory_ids=memory_ids,
        source_ids=source_ids,
    )
    ck = brief_cache_key(f"fallback:{query_id}")
    raw_text = call_llm_text(prompt, cache_key=ck)

    return ReflectResult(
        text=raw_text,
        memory_ids=memory_ids[:5],
        source_refs=[SourceRef(source_id=sid) for sid in source_ids[:3]],
    )


_LABEL_MAP: dict[str, EpistemicLabel] = {
    "FACT": EpistemicLabel.FACT,
    "OBSERVATION": EpistemicLabel.OBSERVATION,
    "INFERENCE": EpistemicLabel.INFERENCE,
    "RECOMMENDATION": EpistemicLabel.RECOMMENDATION,
    "fact": EpistemicLabel.FACT,
    "observation": EpistemicLabel.OBSERVATION,
    "inference": EpistemicLabel.INFERENCE,
    "recommendation": EpistemicLabel.RECOMMENDATION,
}


def _parse_reflect_result(
    *,
    reflect_result: ReflectResult,
    recall: RecallBundle,
    decisions: list[Decision],
    used_fallback: bool,
) -> dict[str, Any]:
    raw_text = reflect_result.text.strip()
    if raw_text.startswith("```"):
        raw_text = "\n".join(raw_text.split("\n")[1:])
    if raw_text.endswith("```"):
        raw_text = raw_text[: raw_text.rfind("```")]
    raw_text = raw_text.strip()

    try:
        data = json.loads(raw_text)
        return _hydrate_parsed_json(
            data=data,
            reflect_result=reflect_result,
            recall=recall,
        )
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        logger.warning(
            "Brief synthesis JSON parse failed (%s) — using deterministic extraction",
            exc,
        )
        return _extract_deterministic(
            reflect_result=reflect_result,
            recall=recall,
            decisions=decisions,
        )


def _hydrate_parsed_json(
    *,
    data: dict[str, Any],
    reflect_result: ReflectResult,
    recall: RecallBundle,
) -> dict[str, Any]:
    fallback_memory_ids = reflect_result.memory_ids
    fallback_source_refs = [
        sr.model_dump() if hasattr(sr, "model_dump") else sr
        for sr in reflect_result.source_refs
    ]

    def _to_claim(raw: dict, default_label: EpistemicLabel) -> BriefClaim:
        label_str = raw.get("label", "")
        label = _LABEL_MAP.get(label_str, default_label)

        memory_ids = raw.get("memory_ids") or []
        source_refs_raw = raw.get("source_refs") or []

        if not memory_ids and not source_refs_raw:
            memory_ids = fallback_memory_ids[:2]
            source_refs_raw = fallback_source_refs[:1]

        source_refs = [
            SourceRef(source_id=s["source_id"]) if isinstance(s, dict) else s
            for s in source_refs_raw
        ]
        return BriefClaim(
            text=raw.get("text", ""),
            label=label,
            memory_ids=memory_ids,
            source_refs=source_refs,
        )

    historical_decisions = [
        _to_claim(r, EpistemicLabel.FACT)
        for r in data.get("historical_decisions", [])
        if isinstance(r, dict)
    ]
    observations = [
        _to_claim(r, EpistemicLabel.OBSERVATION)
        for r in data.get("observations", [])
        if isinstance(r, dict)
    ]
    inferences = [
        _to_claim(r, EpistemicLabel.INFERENCE)
        for r in data.get("inferences", [])
        if isinstance(r, dict)
    ]

    rec_raw = data.get("recommendation")
    recommendation = (
        _to_claim(rec_raw, EpistemicLabel.RECOMMENDATION) if rec_raw else None
    )

    return {
        "answer_summary": data.get("answer_summary", ""),
        "historical_decisions": historical_decisions,
        "observations": observations,
        "inferences": inferences,
        "recommendation": recommendation,
    }


def _extract_deterministic(
    *,
    reflect_result: ReflectResult,
    recall: RecallBundle,
    decisions: list[Decision],
) -> dict[str, Any]:
    historical_decisions: list[BriefClaim] = []
    for decision in decisions:
        for reason in decision.reasons:
            source_refs = [
                SourceRef(source_id=sr.source_id) for sr in decision.source_refs[:1]
            ]
            memory_ids = [reason.source_memory_id] if reason.source_memory_id else []
            if memory_ids or source_refs:
                historical_decisions.append(
                    BriefClaim(
                        text=f"[{decision.id}] {reason.statement}",
                        label=EpistemicLabel.FACT,
                        memory_ids=memory_ids,
                        source_refs=source_refs,
                    )
                )

    observations: list[BriefClaim] = []
    if recall:
        for mem in recall.memories[:3]:
            observations.append(
                BriefClaim(
                    text=mem.text,
                    label=EpistemicLabel.OBSERVATION,
                    memory_ids=[mem.memory_id],
                    source_refs=list(mem.source_refs[:1]),
                )
            )

    answer_text = (
        reflect_result.text[:300]
        if reflect_result.text
        else "Unable to synthesize answer."
    )

    return {
        "answer_summary": answer_text,
        "historical_decisions": historical_decisions,
        "observations": observations,
        "inferences": [],
        "recommendation": None,
    }


def _filter_cited(claims: list[BriefClaim], section: str) -> list[BriefClaim]:
    cited = []
    dropped = 0
    for claim in claims:
        if claim.source_refs or claim.memory_ids:
            cited.append(claim)
        else:
            dropped += 1
            logger.warning(
                "Dropping uncited claim from section=%r: %r",
                section,
                claim.text[:80],
            )
    if dropped:
        logger.warning(
            "Dropped %d uncited claim(s) from section=%r",
            dropped,
            section,
        )
    return cited


def _get_recommendation(
    parsed: dict[str, Any],
    drift_results: list[DriftResult],
) -> BriefClaim:
    llm_rec = parsed.get("recommendation")
    if llm_rec and isinstance(llm_rec, BriefClaim):
        if llm_rec.label == EpistemicLabel.RECOMMENDATION:
            return llm_rec
    return _build_deterministic_recommendation(drift_results)


def _build_deterministic_recommendation(drift_results: list[DriftResult]) -> BriefClaim:
    best = _best_drift(drift_results)
    if best and best.reconsideration_warranted:
        level_text = best.level.value
        text = (
            f"The foundational constraints of the original decision have drifted "
            f"significantly (drift level: {level_text}, score: {best.score:.2f}). "
            f"The premises that drove the original choice have materially changed. "
            f"Reconsideration warranted."
        )
    elif best and best.score > 0:
        text = (
            f"Some constraints have shifted (drift score: {best.score:.2f}, "
            f"level: {best.level.value}), but the foundational premises of the "
            f"original decision largely hold. Original decision holds."
        )
    else:
        text = (
            "The current project context aligns with the foundational premises of "
            "the original decision. Original decision holds."
        )

    return BriefClaim(
        text=text,
        label=EpistemicLabel.RECOMMENDATION,
        memory_ids=[],
        source_refs=[],
    )


def _best_drift(drift_results: list[DriftResult]) -> DriftResult | None:
    if not drift_results:
        return None
    return max(drift_results, key=lambda dr: dr.score)


def _build_confidence(
    *,
    decisions: list[Decision],
    recall: RecallBundle,
    drift_results: list[DriftResult],
) -> ConfidenceBreakdown:
    extraction = None
    if decisions:
        confidences = [
            d.extraction_confidence
            for d in decisions
            if d.extraction_confidence is not None
        ]
        if confidences:
            extraction = min(confidences)

    retrieval = recall.retrieval_confidence if recall else None

    drift = None
    best = _best_drift(drift_results)
    if best:
        drift = best.drift_confidence

    return ConfidenceBreakdown(
        extraction=extraction,
        retrieval=retrieval,
        drift=drift,
        causal=None,
    )


def _collect_source_ids(recall: RecallBundle, decisions: list[Decision]) -> list[str]:
    ids: list[str] = []
    if recall:
        for mem in recall.memories:
            for sr in mem.source_refs:
                if sr.source_id not in ids:
                    ids.append(sr.source_id)
    for decision in decisions:
        for sr in decision.source_refs:
            if sr.source_id not in ids:
                ids.append(sr.source_id)
    return ids


def _collect_all_sources(
    recall: RecallBundle,
    decisions: list[Decision],
    reflect_result: ReflectResult | None,
) -> list[SourceRef]:
    seen: set[str] = set()
    sources: list[SourceRef] = []

    def _add(sr: SourceRef) -> None:
        if sr.source_id not in seen:
            seen.add(sr.source_id)
            sources.append(sr)

    if recall:
        for mem in recall.memories:
            for sr in mem.source_refs:
                _add(sr)
    for decision in decisions:
        for sr in decision.source_refs:
            _add(sr)
    if reflect_result:
        for sr in reflect_result.source_refs:
            _add(sr)

    return sources


def _minimal_safe_brief(
    *,
    query_id: str,
    query: str,
    project_id: str,
    error_message: str,
) -> DecisionBrief:
    warning_claim = BriefClaim(
        text=f"Brief generation encountered an unexpected error: {error_message[:200]}",
        label=EpistemicLabel.OBSERVATION,
        memory_ids=[],
        source_refs=[],
    )
    recommendation = BriefClaim(
        text="Unable to assess reconsideration. Manual review required. Original decision holds.",
        label=EpistemicLabel.RECOMMENDATION,
        memory_ids=[],
        source_refs=[],
    )
    return DecisionBrief(
        query_id=query_id,
        query=query,
        project_id=project_id,
        answer_summary="Brief generation failed. See observations for details.",
        historical_decisions=[],
        historical_constraints=[],
        current_constraints=[],
        constraint_differences=[],
        observations=[warning_claim],
        inferences=[],
        drift=None,
        reconsideration_warranted=False,
        recommendation=recommendation,
        confidence=ConfidenceBreakdown(),
        sources=[],
        generated_at=datetime.now(UTC).isoformat(),
    )
