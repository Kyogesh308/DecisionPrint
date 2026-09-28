"""
Local evaluation models — not part of the shared contracts.
EvaluationReport exists only inside eval/; nothing outside eval/ imports it.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass
class ExtractionMetrics:
    """Per-decision-field accuracy scores."""
    statement_accuracy: float        # token F1 between predicted and gold decision_statement
    constraint_precision: float      # predicted constraints that appear in gold
    constraint_recall: float         # gold constraints found in predicted
    constraint_f1: float
    reason_linked_accuracy: float    # fraction of is_reason_linked flags correct
    needs_review_accuracy: float     # fraction of needs_review flags correct
    n_decisions_evaluated: int


@dataclass
class RetrievalMetrics:
    """How often the correct decision appears in the top-K recalled results."""
    top_1_accuracy: float
    top_3_accuracy: float
    n_questions_evaluated: int


@dataclass
class DriftMetrics:
    """Drift-level classification quality."""
    macro_f1: float
    per_level_f1: dict[str, float]   # keys: none, low, medium, high
    reconsideration_accuracy: float
    n_cases_evaluated: int


@dataclass
class AttributionMetrics:
    """Fraction of BriefClaims that have at least one source reference."""
    attribution_rate: float          # claims with >= 1 citation / total claims
    hallucination_rate: float        # claims with 0 citations / total claims
    n_claims_evaluated: int


@dataclass
class CausalMetrics:
    """Precision of causal link classification against gold labels."""
    label_accuracy: float
    none_precision: float
    non_none_precision: float        # explicit + strong + possible vs none
    n_cases_evaluated: int


@dataclass
class EvaluationReport:
    """
    Full evaluation output. Local to eval/ — never crosses into contracts/.
    generated_at is UTC. All metrics fields are populated by run_evaluation.
    """
    generated_at: datetime = field(default_factory=lambda: datetime.now(tz=UTC))
    gold_dir: str = ""
    pipeline_mode: str = "fixture"   # fixture | live
    n_questions: int = 0

    extraction: ExtractionMetrics | None = None
    retrieval: RetrievalMetrics | None = None
    drift: DriftMetrics | None = None
    attribution: AttributionMetrics | None = None
    causal: CausalMetrics | None = None

    warnings: list[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        """Flatten to a dict suitable for pandas DataFrame construction."""
        return {
            "generated_at": self.generated_at.isoformat(),
            "gold_dir": self.gold_dir,
            "pipeline_mode": self.pipeline_mode,
            "n_questions": self.n_questions,
            # Extraction
            "extraction.statement_accuracy": self.extraction.statement_accuracy if self.extraction else None,
            "extraction.constraint_f1": self.extraction.constraint_f1 if self.extraction else None,
            "extraction.reason_linked_accuracy": self.extraction.reason_linked_accuracy if self.extraction else None,
            # Retrieval
            "retrieval.top_1_accuracy": self.retrieval.top_1_accuracy if self.retrieval else None,
            "retrieval.top_3_accuracy": self.retrieval.top_3_accuracy if self.retrieval else None,
            # Drift
            "drift.macro_f1": self.drift.macro_f1 if self.drift else None,
            "drift.reconsideration_accuracy": self.drift.reconsideration_accuracy if self.drift else None,
            # Attribution
            "attribution.rate": self.attribution.attribution_rate if self.attribution else None,
            "hallucination.rate": self.attribution.hallucination_rate if self.attribution else None,
            # Causal
            "causal.label_accuracy": self.causal.label_accuracy if self.causal else None,
            "causal.non_none_precision": self.causal.non_none_precision if self.causal else None,
        }
