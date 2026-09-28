"""
Evaluation runner — orchestrates all metrics into a single EvaluationReport.
"""
from __future__ import annotations

import json
import logging
import os
from datetime import UTC
from pathlib import Path

import pandas as pd

from contracts.models import Decision
from eval.baseline import run_baseline_rag
from eval.metrics import (
    compute_attribution_metrics,
    compute_causal_metrics,
    compute_drift_f1_detailed,
    score_extraction,
)
from eval.models import EvaluationReport, ExtractionMetrics, RetrievalMetrics
from eval.pipeline import run_decisionprint_pipeline

logger = logging.getLogger("decisionprint.eval.runner")


def run_evaluation(gold_dir: str) -> EvaluationReport:
    """
    Run the full evaluation suite against gold data in gold_dir.
    Returns an EvaluationReport. Also prints a pandas summary table to stdout.

    This is an internal demo evaluation. Do not interpret results as statistically
    significant; the gold set is 15–25 questions.
    """
    report = EvaluationReport(
        gold_dir=gold_dir,
        pipeline_mode=os.environ.get("DP_BACKEND", "fixture"),
    )

    gold_path = Path(gold_dir)
    if not gold_path.exists():
        report.warnings.append(f"gold_dir '{gold_dir}' does not exist")
        _print_report(report)
        return report

    # ------------------------------------------------------------------ #
    # Load gold files                                                       #
    # ------------------------------------------------------------------ #
    eval_questions = _load_json(gold_path / "eval_questions.json", default=[])
    gold_decisions_raw = _load_json(gold_path / "decisions.json", default=[])
    gold_drift_cases = _load_json(gold_path / "drift_cases.json", default=[])
    gold_causal_links = _load_json(gold_path / "causal_links.json", default=[])

    report.n_questions = len(eval_questions)

    if not eval_questions:
        report.warnings.append("eval_questions.json is empty — no metrics computed")
        _print_report(report)
        return report

    # ------------------------------------------------------------------ #
    # 1. Extraction metrics                                                #
    # ------------------------------------------------------------------ #
    report.extraction = _run_extraction_eval(gold_decisions_raw)

    # ------------------------------------------------------------------ #
    # 2. Retrieval top-1 / top-3                                          #
    # ------------------------------------------------------------------ #
    report.retrieval = _run_retrieval_eval(eval_questions)

    # ------------------------------------------------------------------ #
    # 3. Drift F1                                                         #
    # ------------------------------------------------------------------ #
    if gold_drift_cases:
        drift_cases_with_predictions = _run_drift_eval(gold_drift_cases)
        report.drift = compute_drift_f1_detailed(drift_cases_with_predictions)
    else:
        report.warnings.append("drift_cases.json empty — drift metrics skipped")

    # ------------------------------------------------------------------ #
    # 4. Attribution / hallucination                                      #
    # ------------------------------------------------------------------ #
    report.attribution = _run_attribution_eval(eval_questions)

    # ------------------------------------------------------------------ #
    # 5. Causal precision                                                 #
    # ------------------------------------------------------------------ #
    if gold_causal_links:
        report.causal = _run_causal_eval(gold_causal_links)
    else:
        report.warnings.append("causal_links.json empty — causal metrics skipped")

    _print_report(report)
    return report


# --------------------------------------------------------------------------- #
# Sub-evaluators                                                               #
# --------------------------------------------------------------------------- #

def _run_extraction_eval(gold_decisions_raw: list[dict]) -> ExtractionMetrics | None:
    """
    Run extract_decisions on the gold source texts, then compare to gold decisions.
    In fixture mode we compare fixture decisions instead — live extraction requires
    P3's data files to be present.
    """
    if not gold_decisions_raw:
        return None

    # Build gold Decision objects from raw dicts (fields we care about)
    gold_decisions: list[Decision] = []
    for raw in gold_decisions_raw:
        try:
            gold_decisions.append(_partial_decision_from_raw(raw))
        except Exception as exc:
            logger.warning("Skipping malformed gold decision: %s", exc)

    if not gold_decisions:
        return None

    # Get predicted decisions — fixture mode returns P3's fixture decisions
    predicted = _get_predicted_decisions(gold_decisions)

    scores = score_extraction(predicted, gold_decisions)
    return ExtractionMetrics(
        statement_accuracy=scores["statement_accuracy"],
        constraint_precision=scores["constraint_precision"],
        constraint_recall=scores["constraint_recall"],
        constraint_f1=scores["constraint_f1"],
        reason_linked_accuracy=scores["reason_linked_accuracy"],
        needs_review_accuracy=0.0,     # not in gold schema
        n_decisions_evaluated=int(scores["n_evaluated"]),
    )


def _run_retrieval_eval(eval_questions: list[dict]) -> RetrievalMetrics:
    """
    For each question: run baseline_rag and check whether the expected decision IDs
    appear in the retrieved text. This approximates top-K retrieval accuracy.
    """
    data_dir = os.environ.get("DP_DATA_DIR", "./data")
    top1_hits = 0
    top3_hits = 0
    total = 0

    for q in eval_questions:
        expected_ids: list[str] = q.get("expected_decision_ids") or []
        if not expected_ids:
            continue

        total += 1
        top1_result = run_baseline_rag(q["question"], data_dir=data_dir, top_k=1)
        top3_result = run_baseline_rag(q["question"], data_dir=data_dir, top_k=3)

        if any(did in top1_result for did in expected_ids):
            top1_hits += 1
        if any(did in top3_result for did in expected_ids):
            top3_hits += 1

    if total == 0:
        return RetrievalMetrics(top_1_accuracy=0.0, top_3_accuracy=0.0, n_questions_evaluated=0)

    return RetrievalMetrics(
        top_1_accuracy=top1_hits / total,
        top_3_accuracy=top3_hits / total,
        n_questions_evaluated=total,
    )


def _run_drift_eval(gold_drift_cases: list[dict]) -> list[dict]:
    """
    For each drift case, run the drift engine with fixture decisions and current context,
    then attach the predicted level and reconsideration_warranted.
    """
    from intelligence import compare_constraints, normalize_constraints, score_drift

    enriched: list[dict] = []
    for case in gold_drift_cases:
        try:
            pred_level, pred_rec = _predict_drift_for_case(
                case, compare_constraints, normalize_constraints, score_drift
            )
            enriched.append({
                **case,
                "predicted_level": pred_level,
                "predicted_reconsideration_warranted": pred_rec,
            })
        except Exception as exc:
            logger.warning("Drift eval failed for case %s: %s", case.get("case_id"), exc)
            enriched.append({
                **case,
                "predicted_level": "none",
                "predicted_reconsideration_warranted": False,
            })

    return enriched


def _predict_drift_for_case(case: dict, compare_constraints, normalize_constraints, score_drift):
    """
    Load fixture decision + fixture current context for this case,
    run the drift engine, return (predicted_level, predicted_reconsideration).
    """
    # Load fixture objects — these are the same objects used in tests
    decision = _get_fixture_decision(case["decision_id"])
    current = _get_fixture_context(case["current_project_id"])

    if decision is None or current is None:
        return "none", False

    delta = compare_constraints(decision, current)
    result = score_drift(delta)
    return result.level.value, result.reconsideration_warranted


def _run_attribution_eval(eval_questions: list[dict]) -> None:
    """
    Run the pipeline for each question and measure citation coverage.
    In fixture mode: uses the single fixture brief repeated for all questions.
    In live mode: calls ask_question for each.
    """

    briefs = []
    for q in eval_questions:
        try:
            brief = run_decisionprint_pipeline(
                q["question"],
                project_id=q.get("project_id", "nova"),
            )
            briefs.append(brief)
        except Exception as exc:
            logger.warning("Pipeline failed for question '%s': %s", q.get("question_id"), exc)

    if not briefs:
        return None

    return compute_attribution_metrics(briefs)


def _run_causal_eval(gold_causal_links: list[dict]) -> None:
    """
    For each gold causal case: get the predicted label from fixture or live classifier.
    """
    from intelligence import classify_causal_link

    predicted = []
    for case in gold_causal_links:
        try:
            pred_link = _predict_causal_for_case(case, classify_causal_link)
            predicted.append({
                "decision_id": case["decision_id"],
                "outcome_id": case["outcome_id"],
                "label": pred_link.label.value,
            })
        except Exception as exc:
            logger.warning("Causal eval failed for case %s: %s", case.get("case_id"), exc)
            predicted.append({
                "decision_id": case.get("decision_id"),
                "outcome_id": case.get("outcome_id"),
                "label": "none",
            })

    return compute_causal_metrics(predicted, gold_causal_links)


def _predict_causal_for_case(case: dict, classify_causal_link):
    """Load fixture decision and outcome, run classifier."""
    decision = _get_fixture_decision(case["decision_id"])
    outcome = _get_fixture_outcome(case["outcome_id"])
    evidence = _get_fixture_evidence(case["decision_id"])

    if decision is None or outcome is None:
        from contracts.enums import CausalLabel
        from contracts.models import CausalLink
        return CausalLink(
            decision_id=case["decision_id"],
            outcome_id=case["outcome_id"],
            label=CausalLabel.NONE,
            rationale="Fixture not available",
            evidence_ids=[],
            confidence=0.0,
        )

    return classify_causal_link(decision, outcome, evidence or [])


# --------------------------------------------------------------------------- #
# Fixture loaders                                                               #
# --------------------------------------------------------------------------- #

def _get_fixture_decision(decision_id: str):
    """Load a Decision from test fixtures by ID."""
    import json
    from pathlib import Path
    fixture_path = Path("tests/p2/fixtures/decision_alpha_kafka.json")
    if fixture_path.exists():
        try:
            raw = json.loads(fixture_path.read_text())
            from contracts.models import Decision
            dec = Decision(**raw)
            if dec.id == decision_id:
                return dec
        except Exception:
            pass
    return None


def _get_fixture_context(project_id: str):
    """Load a CurrentProjectContext from test fixtures by project_id."""
    import json
    from pathlib import Path
    fixture_path = Path("tests/p2/fixtures/context_nova.json")
    if fixture_path.exists():
        try:
            raw = json.loads(fixture_path.read_text())
            from contracts.models import CurrentProjectContext
            ctx = CurrentProjectContext(**raw)
            if ctx.project_id == project_id:
                return ctx
        except Exception:
            pass
    return None


def _get_fixture_outcome(outcome_id: str):
    """Load an Outcome from test fixtures by ID."""
    import json
    from pathlib import Path
    for fname in ["recall_bundle_cedar.json"]:
        fp = Path(f"tests/p2/fixtures/{fname}")
        if fp.exists():
            try:
                raw = json.loads(fp.read_text())
                # outcomes may be embedded — best effort
            except Exception:
                pass


def _get_fixture_evidence(decision_id: str):
    """Load evidence memories for a decision from recall bundle fixtures."""
    import json
    from pathlib import Path
    bundle_path = Path("tests/p2/fixtures/recall_bundle_cedar.json")
    if bundle_path.exists():
        try:
            raw = json.loads(bundle_path.read_text())
            from contracts.models import RecallBundle
            bundle = RecallBundle(**raw)
            return bundle.memories
        except Exception:
            pass
    return []


def _get_predicted_decisions(gold_decisions: list[Decision]) -> list[Decision]:
    """
    Return predicted decisions for eval. In fixture mode, return the Phase 0 fixtures.
    In live mode, would call extract_decisions over the real data files.
    """
    import json
    from pathlib import Path

    from contracts.models import Decision

    fixture_path = Path("tests/p2/fixtures/decision_alpha_kafka.json")
    if fixture_path.exists():
        try:
            raw = json.loads(fixture_path.read_text())
            return [Decision(**raw)]
        except Exception:
            pass
    return []


def _partial_decision_from_raw(raw: dict) -> Decision:
    """
    Build a minimal Decision from a gold JSON dict.
    Gold decisions don't have all fields — populate defaults for missing ones.
    """
    from datetime import datetime

    from contracts.enums import DecisionStatus
    from contracts.models import Constraint, Decision

    constraints = [
        Constraint(
            key=c["key"],
            value=c.get("value"),
            is_reason_linked=c.get("is_reason_linked", False),
        )
        for c in raw.get("constraints", [])
    ]

    return Decision(
        id=raw["id"],
        project_id=raw["project_id"],
        title=raw.get("title", ""),
        decision_statement=raw.get("decision_statement", ""),
        occurred_at=datetime.fromisoformat(raw["occurred_at"]) if raw.get("occurred_at") else datetime.now(tz=UTC),
        participants=[],
        context_summary="",
        constraints=constraints,
        assumptions=[],
        alternatives=[],
        selected_option=raw.get("selected_option", ""),
        reasons=[],
        technologies=[],
        source_refs=[],
        extraction_confidence=1.0,
        outcome_refs=[],
        status=DecisionStatus.ACTIVE,
        superseded_by=None,
        related_decisions=[],
        needs_review=False,
    )


# --------------------------------------------------------------------------- #
# Output                                                                        #
# --------------------------------------------------------------------------- #

def _print_report(report: EvaluationReport) -> None:
    """
    Print a formatted pandas summary table to stdout.
    This is the primary human-readable output of the eval harness.
    """
    print("\n" + "=" * 60)
    print("DecisionPrint — Internal Demo Evaluation")
    print(f"Generated: {report.generated_at.isoformat()}")
    print(f"Mode: {report.pipeline_mode}  |  Questions: {report.n_questions}")
    print("NOTE: Small gold set (15–25 items). Do not claim statistical significance.")
    print("=" * 60)

    rows = []

    if report.extraction:
        e = report.extraction
        rows += [
            ("Extraction", "Statement accuracy (token F1)", f"{e.statement_accuracy:.3f}", f"{e.n_decisions_evaluated} decisions"),
            ("Extraction", "Constraint F1", f"{e.constraint_f1:.3f}", ""),
            ("Extraction", "Constraint precision", f"{e.constraint_precision:.3f}", ""),
            ("Extraction", "Constraint recall", f"{e.constraint_recall:.3f}", ""),
            ("Extraction", "is_reason_linked accuracy", f"{e.reason_linked_accuracy:.3f}", ""),
        ]

    if report.retrieval:
        r = report.retrieval
        rows += [
            ("Retrieval", "Top-1 accuracy", f"{r.top_1_accuracy:.3f}", f"{r.n_questions_evaluated} questions"),
            ("Retrieval", "Top-3 accuracy", f"{r.top_3_accuracy:.3f}", ""),
        ]

    if report.drift:
        d = report.drift
        rows += [
            ("Drift", "Macro F1", f"{d.macro_f1:.3f}", f"{d.n_cases_evaluated} cases"),
            ("Drift", "Reconsideration accuracy", f"{d.reconsideration_accuracy:.3f}", ""),
        ] + [
            ("Drift", f"  F1 [{level}]", f"{f1:.3f}", "")
            for level, f1 in d.per_level_f1.items()
        ]

    if report.attribution:
        a = report.attribution
        rows += [
            ("Attribution", "Citation rate", f"{a.attribution_rate:.3f}", f"{a.n_claims_evaluated} claims"),
            ("Attribution", "Hallucination rate", f"{a.hallucination_rate:.3f}", ""),
        ]

    if report.causal:
        c = report.causal
        rows += [
            ("Causal", "Label accuracy", f"{c.label_accuracy:.3f}", f"{c.n_cases_evaluated} cases"),
            ("Causal", "Non-none precision", f"{c.non_none_precision:.3f}", ""),
        ]

    df = pd.DataFrame(rows, columns=["Category", "Metric", "Score", "Notes"])
    print(df.to_string(index=False))

    if report.warnings:
        print("\nWarnings:")
        for w in report.warnings:
            print(f"  ⚠ {w}")

    print("=" * 60 + "\n")


# --------------------------------------------------------------------------- #
# Helpers                                                                       #
# --------------------------------------------------------------------------- #

def _load_json(path: Path, *, default) -> list | dict:
    if not path.exists():
        logger.warning("Gold file not found: %s", path)
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        logger.warning("Could not load '%s': %s", path, exc)
        return default
