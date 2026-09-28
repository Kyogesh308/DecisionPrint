from datetime import datetime, timezone
from typing import Any

from contracts.models import (
    DecisionBrief, BriefClaim, ConfidenceBreakdown, SourceRef,
    Decision, ProjectContext, RecallBundle, MemoryKind
)
from contracts.enums import EpistemicLabel, DriftLevel

from .brief_guards import (
    REFLECT_FALLBACK_NOTICE, NO_CURRENT_CONTEXT_NOTICE, NO_EVIDENCE_NOTICE, NO_COMPARABLE_NOTICE
)
from .drift import score_drift, compare_constraints

def _dedupe_refs(refs: list[SourceRef]) -> list[SourceRef]:
    def ref_key(r): return (r.source_id, getattr(r, "document_id", "") or "", getattr(r, "chunk_id", "") or "", getattr(r, "locator", "") or "")
    out = []
    seen = set()
    for r in refs:
        k = ref_key(r)
        if k not in seen:
            seen.add(k)
            out.append(r)
    return sorted(out, key=ref_key)

def build_deterministic_brief(
    query_id: str,
    query: str,
    scope: Any,
    recall: RecallBundle,
    decisions: list[Decision],
    current: ProjectContext | None,
    reflect_failed: bool = False
) -> DecisionBrief:
    # 1. State
    results = [score_drift(compare_constraints(d, current)) for d in decisions] if current else []
    decisions_by_id = {d.id: d for d in decisions}
    
    def rank(r):
        d = decisions_by_id[r.decision_id]
        occ = d.occurred_at if d.occurred_at else datetime.now(timezone.utc)
        return (not r.reconsideration_warranted, -r.score, -r.drift_confidence,
                -occ.timestamp(), r.decision_id)
    
    primary_res = min(results, key=rank) if results else None
    primary_dec = decisions_by_id[primary_res.decision_id] if primary_res else None

    # Templates
    if not recall.memories and not decisions:
        answer_summary = "No relevant historical evidence was found."
        rec_text = "No relevant historical evidence was found; nothing here supports or opposes any option."
        notices = [NO_EVIDENCE_NOTICE]
    elif not current:
        answer_summary = f"Found {len(decisions)} historical decision(s), but missing current context to assess drift."
        rec_text = "Drift could not be assessed (missing or non-comparable constraints). Add current project constraints to enable comparison."
        notices = [NO_CURRENT_CONTEXT_NOTICE]
    elif primary_res and primary_res.level == DriftLevel.none:
        answer_summary = f"Assessed drift against '{primary_dec.title}', but constraints are incomparable."
        rec_text = "Drift could not be assessed (missing or non-comparable constraints). Add current project constraints to enable comparison."
        notices = [NO_COMPARABLE_NOTICE]
    elif primary_res and primary_res.reconsideration_warranted:
        answer_summary = f"Found drift against historical decision '{primary_dec.title}' indicating reconsideration may be warranted."
        rec_text = "Reconsideration warranted: the premises behind this historical decision differ materially from the current context. Review the constraint differences and evidence; the decision remains with the team."
        notices = []
    else:
        answer_summary = f"Assessed drift against '{primary_dec.title}'. Drift is low; premises hold."
        rec_text = "The constraint comparison does not currently indicate reconsideration. Confirm with the team before relying on this."
        notices = []

    if reflect_failed:
        notices.append(REFLECT_FALLBACK_NOTICE)

    # Build Claims
    hist_decisions = []
    for d in decisions:
        mids = set()
        for r in d.reasons:
            if r.source_memory_id: mids.add(r.source_memory_id)
        for c in d.constraints:
            if c.source_memory_id: mids.add(c.source_memory_id)
        hist_decisions.append(BriefClaim(
            text=f"{d.decision_statement} {d.reasons[0].statement if d.reasons else ''}".strip(),
            label=EpistemicLabel.FACT,
            source_refs=d.source_refs,
            memory_ids=sorted(mids)
        ))

    observations = []
    obs_mems = sorted([m for m in recall.memories if m.kind == MemoryKind.observation], 
                      key=lambda x: (-x.relevance, x.memory_id))[:5]
    for m in obs_mems:
        observations.append(BriefClaim(
            text=m.summary, label=EpistemicLabel.OBSERVATION, memory_ids=[m.memory_id], source_refs=m.source_refs
        ))
    for n in notices:
        observations.append(BriefClaim(
            text=n, label=EpistemicLabel.OBSERVATION, memory_ids=[], source_refs=[]
        ))

    inferences = []
    if primary_res and primary_res.changed:
        changes = []
        for d in primary_res.changed:
            changes.append(f"{d.key} {d.historical_value} \u2192 {d.current_value}")
        inferences.append(BriefClaim(
            text="Changed reason-linked premises: " + "; ".join(changes),
            label=EpistemicLabel.INFERENCE,
            source_refs=primary_dec.source_refs,
            memory_ids=[]
        ))
    
    # Confidence
    ext = min([d.extraction_confidence for d in decisions]) if decisions else None
    ret = max(0.0, min(1.0, recall.retrieval_confidence))
    drf = primary_res.drift_confidence if primary_res else None

    # Sources
    sources = _dedupe_refs([r for d in decisions for r in d.source_refs] + [r for m in recall.memories for r in m.source_refs])

    return DecisionBrief(
        query_id=query_id,
        query=query,
        project_id=current.project_id if current else "unknown",
        answer_summary=answer_summary,
        historical_decisions=hist_decisions,
        historical_constraints=primary_dec.constraints if primary_dec else [],
        current_constraints=current.constraints if current else [],
        constraint_differences=[primary_res] if primary_res else [],
        observations=observations,
        inferences=inferences,
        drift=primary_res,
        reconsideration_warranted=primary_res.reconsideration_warranted if primary_res else False,
        recommendation=BriefClaim(
            text=rec_text, label=EpistemicLabel.RECOMMENDATION, source_refs=primary_dec.source_refs if primary_dec else [], memory_ids=[]
        ),
        confidence=ConfidenceBreakdown(extraction=ext, retrieval=ret, drift=drf, causal=None),
        sources=sources,
        generated_at=datetime.now(timezone.utc).isoformat()
    )
