"""
Metric computation functions for the DecisionPrint evaluation harness.
All functions are pure — no LLM calls, no I/O, no side effects.
"""
from __future__ import annotations

import logging
import re
from collections import Counter

from contracts.enums import DriftLevel
from contracts.models import BriefClaim, Decision
from eval.models import (
    AttributionMetrics,
    CausalMetrics,
    DriftMetrics,
)

logger = logging.getLogger("decisionprint.eval.metrics")


# --------------------------------------------------------------------------- #
# score_extraction                                                              #
# --------------------------------------------------------------------------- #

def score_extraction(
    predicted: list[Decision],
    gold: list[Decision],
) -> dict[str, float]:
    """
    Compare predicted Decision objects against gold decisions.
    Matches by project_id first, then aligns by closest statement similarity.
    Returns a dict of metric name → float score (all in [0, 1]).
    """
    if not gold:
        logger.warning("score_extraction: gold list is empty")
        return _zero_extraction_scores()

    # Build gold index by decision id (if IDs match) or by project
    gold_by_id = {d.id: d for d in gold}
    pred_by_id = {d.id: d for d in predicted}

    statement_scores: list[float] = []
    constraint_precisions: list[float] = []
    constraint_recalls: list[float] = []
    reason_linked_scores: list[float] = []
    needs_review_scores: list[float] = []

    for gold_dec in gold:
        pred_dec = _find_best_match(gold_dec, predicted, gold_by_id, pred_by_id)
        if pred_dec is None:
            # Missing decision counts as zeros across all metrics for that decision
            statement_scores.append(0.0)
            constraint_precisions.append(0.0)
            constraint_recalls.append(0.0)
            reason_linked_scores.append(0.0)
            needs_review_scores.append(0.0)
            continue

        statement_scores.append(
            _token_f1(pred_dec.decision_statement, gold_dec.decision_statement)
        )
        cp, cr = _constraint_precision_recall(pred_dec, gold_dec)
        constraint_precisions.append(cp)
        constraint_recalls.append(cr)
        reason_linked_scores.append(_reason_linked_accuracy(pred_dec, gold_dec))
        # needs_review: gold doesn't prescribe it — skip if no gold field exists
        # (gold decisions may not have extraction_confidence < 0.60 logic applied)

    n = len(gold)
    avg_precision = sum(constraint_precisions) / n
    avg_recall = sum(constraint_recalls) / n
    constraint_f1 = (
        2 * avg_precision * avg_recall / (avg_precision + avg_recall)
        if (avg_precision + avg_recall) > 0 else 0.0
    )

    return {
        "statement_accuracy": sum(statement_scores) / n,
        "constraint_precision": avg_precision,
        "constraint_recall": avg_recall,
        "constraint_f1": constraint_f1,
        "reason_linked_accuracy": sum(reason_linked_scores) / n,
        "n_evaluated": float(n),
    }


def _find_best_match(
    gold_dec: Decision,
    predicted: list[Decision],
    gold_by_id: dict,
    pred_by_id: dict,
) -> Decision | None:
    """
    Match a gold decision to a predicted decision.
    Preference order: exact ID match → same project + highest statement similarity.
    """
    if gold_dec.id in pred_by_id:
        return pred_by_id[gold_dec.id]

    # Fall back to best statement match within the same project
    candidates = [p for p in predicted if p.project_id == gold_dec.project_id]
    if not candidates:
        return None
    return max(candidates, key=lambda p: _token_f1(p.decision_statement, gold_dec.decision_statement))


def _token_f1(predicted_text: str, gold_text: str) -> float:
    """
    Token-level F1 between two strings (standard QA metric).
    Ignores punctuation; case-insensitive.
    """
    pred_tokens = Counter(_tokenize(predicted_text))
    gold_tokens = Counter(_tokenize(gold_text))

    common = sum((pred_tokens & gold_tokens).values())
    if common == 0:
        return 0.0
    precision = common / sum(pred_tokens.values())
    recall = common / sum(gold_tokens.values())
    return 2 * precision * recall / (precision + recall)


def _tokenize(text: str) -> list[str]:
    return re.findall(r"\b[a-z]{2,}\b", text.lower())


def _constraint_precision_recall(pred: Decision, gold: Decision) -> tuple[float, float]:
    """
    Precision/recall on (key, normalized_value) constraint pairs.
    Gold constraints are drawn from gold.constraints; values compared as lowercase strings.
    """
    gold_pairs = {(c.key, str(c.value or "").lower()) for c in gold.constraints}
    pred_pairs = {(c.key, str(c.value or "").lower()) for c in pred.constraints}

    if not gold_pairs:
        return (1.0, 1.0) if not pred_pairs else (0.0, 1.0)
    if not pred_pairs:
        return (1.0, 0.0)

    true_positives = len(gold_pairs & pred_pairs)
    precision = true_positives / len(pred_pairs)
    recall = true_positives / len(gold_pairs)
    return precision, recall


def _reason_linked_accuracy(pred: Decision, gold: Decision) -> float:
    """
    Fraction of constraints where is_reason_linked matches between pred and gold.
    Matches constraints by key.
    """
    gold_map = {c.key: c.is_reason_linked for c in gold.constraints}
    pred_map = {c.key: c.is_reason_linked for c in pred.constraints}

    shared_keys = set(gold_map) & set(pred_map)
    if not shared_keys:
        return 1.0   # vacuously correct if no shared keys

    correct = sum(1 for k in shared_keys if gold_map[k] == pred_map[k])
    return correct / len(shared_keys)


def _zero_extraction_scores() -> dict[str, float]:
    return {
        "statement_accuracy": 0.0,
        "constraint_precision": 0.0,
        "constraint_recall": 0.0,
        "constraint_f1": 0.0,
        "reason_linked_accuracy": 0.0,
        "n_evaluated": 0.0,
    }


# --------------------------------------------------------------------------- #
# compute_drift_f1                                                              #
# --------------------------------------------------------------------------- #

def compute_drift_f1(cases: list[dict]) -> float:
    """
    Compute macro-averaged F1 across DriftLevel classes.

    cases: list of dicts with keys:
      - predicted_level: str (DriftLevel value)
      - gold_level: str (DriftLevel value)
    Returns macro F1 (float in [0, 1]).
    """
    if not cases:
        logger.warning("compute_drift_f1: no cases provided")
        return 0.0

    labels = [level.value for level in DriftLevel]
    tp = {l: 0 for l in labels}
    fp = {l: 0 for l in labels}
    fn = {l: 0 for l in labels}

    for case in cases:
        pred = str(case.get("predicted_level") or "none").lower()
        gold = str(case.get("gold_level") or "none").lower()

        if pred not in labels:
            pred = "none"
        if gold not in labels:
            gold = "none"

        if pred == gold:
            tp[pred] += 1
        else:
            fp[pred] += 1
            fn[gold] += 1

    f1_per_class: dict[str, float] = {}
    for label in labels:
        if tp[label] + fp[label] + fn[label] == 0:
            f1_per_class[label] = 1.0
            continue
        precision = tp[label] / (tp[label] + fp[label]) if (tp[label] + fp[label]) > 0 else 0.0
        recall = tp[label] / (tp[label] + fn[label]) if (tp[label] + fn[label]) > 0 else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
        f1_per_class[label] = f1

    macro_f1 = sum(f1_per_class.values()) / len(labels)
    return macro_f1


def compute_drift_f1_detailed(cases: list[dict]) -> DriftMetrics:
    """
    Extended drift metrics including per-level F1 and reconsideration accuracy.
    """
    if not cases:
        return DriftMetrics(
            macro_f1=0.0,
            per_level_f1={l.value: 0.0 for l in DriftLevel},
            reconsideration_accuracy=0.0,
            n_cases_evaluated=0,
        )

    labels = [level.value for level in DriftLevel]
    tp = {l: 0 for l in labels}
    fp = {l: 0 for l in labels}
    fn = {l: 0 for l in labels}

    reconsideration_correct = 0
    reconsideration_total = 0

    for case in cases:
        pred_level = str(case.get("predicted_level") or "none").lower()
        gold_level = str(case.get("gold_level") or "none").lower()
        if pred_level not in labels:
            pred_level = "none"
        if gold_level not in labels:
            gold_level = "none"

        if pred_level == gold_level:
            tp[pred_level] += 1
        else:
            fp[pred_level] += 1
            fn[gold_level] += 1

        # Reconsideration accuracy
        if "gold_reconsideration_warranted" in case:
            reconsideration_total += 1
            pred_rec = bool(case.get("predicted_reconsideration_warranted", False))
            gold_rec = bool(case["gold_reconsideration_warranted"])
            if pred_rec == gold_rec:
                reconsideration_correct += 1

    per_level_f1: dict[str, float] = {}
    for label in labels:
        if tp[label] + fp[label] + fn[label] == 0:
            per_level_f1[label] = 1.0
            continue
        p = tp[label] / (tp[label] + fp[label]) if (tp[label] + fp[label]) > 0 else 0.0
        r = tp[label] / (tp[label] + fn[label]) if (tp[label] + fn[label]) > 0 else 0.0
        per_level_f1[label] = 2 * p * r / (p + r) if (p + r) > 0 else 0.0

    return DriftMetrics(
        macro_f1=sum(per_level_f1.values()) / len(labels),
        per_level_f1=per_level_f1,
        reconsideration_accuracy=(
            reconsideration_correct / reconsideration_total if reconsideration_total > 0 else 0.0
        ),
        n_cases_evaluated=len(cases),
    )


# --------------------------------------------------------------------------- #
# Attribution / hallucination                                                  #
# --------------------------------------------------------------------------- #

def compute_attribution_metrics(briefs) -> AttributionMetrics:
    """
    Compute attribution rate and hallucination rate across a list of DecisionBrief objects.
    A claim is attributed if it has at least one source_ref OR at least one memory_id.
    """
    total_claims = 0
    attributed_claims = 0

    for brief in briefs:
        all_claims: list[BriefClaim] = (
            brief.historical_decisions
            + brief.observations
            + brief.inferences
            + [brief.recommendation]
        )
        for claim in all_claims:
            total_claims += 1
            has_ref = bool(claim.source_refs) or bool(claim.memory_ids)
            if has_ref:
                attributed_claims += 1

    if total_claims == 0:
        return AttributionMetrics(
            attribution_rate=1.0,
            hallucination_rate=0.0,
            n_claims_evaluated=0,
        )

    attribution_rate = attributed_claims / total_claims
    return AttributionMetrics(
        attribution_rate=attribution_rate,
        hallucination_rate=1.0 - attribution_rate,
        n_claims_evaluated=total_claims,
    )


# --------------------------------------------------------------------------- #
# Causal precision                                                              #
# --------------------------------------------------------------------------- #

def compute_causal_metrics(
    predicted_links: list[dict],
    gold_links: list[dict],
) -> CausalMetrics:
    """
    predicted_links and gold_links: each a list of dicts with keys:
      decision_id, outcome_id, label
    Matches by (decision_id, outcome_id) pair.
    """
    gold_map = {
        (item["decision_id"], item["outcome_id"]): str(item["gold_label"]).lower()
        for item in gold_links
    }

    correct = 0
    total = 0
    non_none_correct = 0
    non_none_total = 0

    for pred in predicted_links:
        key = (pred.get("decision_id"), pred.get("outcome_id"))
        if key not in gold_map:
            continue

        gold_label = gold_map[key]
        pred_label = str(pred.get("label") or "none").lower()
        total += 1

        if pred_label == gold_label:
            correct += 1

        if gold_label != "none":
            non_none_total += 1
            if pred_label == gold_label:
                non_none_correct += 1

    return CausalMetrics(
        label_accuracy=correct / total if total > 0 else 0.0,
        none_precision=0.0,      # can compute if needed
        non_none_precision=non_none_correct / non_none_total if non_none_total > 0 else 0.0,
        n_cases_evaluated=total,
    )
