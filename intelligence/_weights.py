"""
intelligence/_weights.py

Local constants for drift scoring. These mirror contracts.constants — do not
invent new values here. If contracts.constants changes, update this file too.
"""

# Constraint weights
REASON_LINKED_WEIGHT: float = 1.0
NON_REASON_LINKED_WEIGHT: float = 0.25

# Drift score → level thresholds (lower bound inclusive, upper exclusive)
# Order matters: check from high → low.
DRIFT_THRESHOLDS: list[tuple[str, float, float]] = [
    ("high", 0.70, float("inf")),
    ("medium", 0.40, 0.70),
    ("low", 0.15, 0.40),
    ("none", 0.00, 0.15),
]

# Reconsideration gate — BOTH must be met
RECONSIDERATION_MIN_SCORE: float = 0.50
RECONSIDERATION_MIN_CONFIDENCE: float = 0.50

# Extraction quality gate (used in Phase 3, referenced here for completeness)
LOW_EXTRACTION_CONFIDENCE: float = 0.60
