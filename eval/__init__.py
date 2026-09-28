"""
Evaluation harness for DecisionPrint.
eval/ is owned by P2. It is eval-only — no product code imports from here.
"""

from eval.baseline import run_baseline_rag
from eval.metrics import compute_drift_f1, score_extraction
from eval.pipeline import run_decisionprint_pipeline
from eval.runner import run_evaluation

__all__ = [
    "compute_drift_f1",
    "run_baseline_rag",
    "run_decisionprint_pipeline",
    "run_evaluation",
    "score_extraction",
]
