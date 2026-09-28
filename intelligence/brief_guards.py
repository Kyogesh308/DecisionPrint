import re
import logging
from typing import Iterable

from contracts.models import DecisionBrief, BriefClaim
from contracts.enums import EpistemicLabel

_LOG = logging.getLogger("decisionprint.intelligence.guards")

REFLECT_FALLBACK_NOTICE = ("Deep synthesis was unavailable, so this brief was built from the "
                           "deterministic constraint comparison and recalled evidence only.")
NO_CURRENT_CONTEXT_NOTICE = ("No current project constraints were provided, so Decision Drift "
                             "could not be assessed.")
NO_EVIDENCE_NOTICE = "No relevant historical evidence was found in the memory you are authorized to see."
NO_COMPARABLE_NOTICE = "Too few comparable constraints to assess drift with confidence."
NOTICE_TEXTS = frozenset({REFLECT_FALLBACK_NOTICE, NO_CURRENT_CONTEXT_NOTICE,
                          NO_EVIDENCE_NOTICE, NO_COMPARABLE_NOTICE})


def _has_reference(c: BriefClaim) -> bool:
    return bool(c.source_refs or c.memory_ids)

def drop_unsupported(claims: list[BriefClaim], section: str) -> list[BriefClaim]:
    kept = [c for c in claims if _has_reference(c) or c.text in NOTICE_TEXTS]
    if len(kept) != len(claims):
        _LOG.warning("dropped %d unsupported claim(s) from %s", len(claims) - len(kept), section)
    return kept

_NEGATION = re.compile(r"(?:\b(?:not|never|avoid|without)\b|n't)", re.IGNORECASE)

def _directive_patterns(techs: set[str]) -> list[re.Pattern]:
    t = "|".join(re.escape(x) for x in sorted(techs))
    return [
        re.compile(rf"\b(?:use|adopt|choose|select|go with|switch to|migrate to|implement|introduce)"
                   rf"\s+(?:apache\s+|the\s+)?(?:{t})\b", re.I),
        re.compile(rf"\b(?:{t})\s+(?:should|must)\s+be\s+(?:used|adopted|chosen|selected)\b", re.I),
        re.compile(rf"\b(?:recommend|suggest)\w*\s+(?:using\s+)?(?:apache\s+)?(?:{t})\b", re.I),
    ]

def find_directive_language(text: str, technologies: Iterable[str]) -> str | None:
    techs = {t.lower() for t in technologies if t}
    if not techs:
        return None
    for sentence in re.split(r"(?<=[.!?])\s+", text):
        for pat in _directive_patterns(techs):
            for m in pat.finditer(sentence):
                if not _NEGATION.search(sentence[max(0, m.start() - 24) : m.start()]):
                    return sentence.strip()
    return None

def _ref_key(r): return (r.source_id, getattr(r, "document_id", "") or "", getattr(r, "chunk_id", "") or "", getattr(r, "locator", "") or "")

def check_brief_invariants(brief: DecisionBrief) -> list[str]:
    problems: list[str] = []
    claims = [("historical_decisions", brief.historical_decisions),
              ("observations", brief.observations), ("inferences", brief.inferences),
              ("recommendation", [brief.recommendation])]
    for name, group in claims:
        for c in group:
            if not _has_reference(c) and c.text not in NOTICE_TEXTS:
                problems.append(f"{name}: uncited claim {c.text[:60]!r}")
    if brief.recommendation.label is not EpistemicLabel.RECOMMENDATION:
        problems.append("recommendation label is not 'recommendation'")
    if brief.drift is None and brief.reconsideration_warranted:
        problems.append("warranted without drift")
    if brief.drift is not None and brief.drift.reconsideration_warranted != brief.reconsideration_warranted:
        problems.append("reconsideration flag disagrees with drift")
    for field in ("extraction", "retrieval", "drift", "causal"):
        v = getattr(brief.confidence, field)
        if v is not None and not 0.0 <= v <= 1.0:
            problems.append(f"confidence.{field} out of range")
    if not brief.answer_summary.strip():
        problems.append("empty answer_summary")
    claim_refs = {_ref_key(r) for _, g in claims for c in g for r in c.source_refs}
    if claim_refs - {_ref_key(r) for r in brief.sources}:
        problems.append("brief.sources is missing refs cited by claims")
    ids = {d.decision_id for d in brief.constraint_differences}
    if brief.drift is not None and brief.drift.decision_id not in ids:
        problems.append("drift decision missing from constraint_differences")
    return problems
