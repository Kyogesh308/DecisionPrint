"""
Per-project sequential ID counter.
Not thread-safe; single-process hackathon scope only.
"""

from __future__ import annotations

from contracts.ids import make_decision_id, make_outcome_id

_decision_counters: dict[str, int] = {}
_outcome_counters: dict[str, int] = {}


def next_decision_id(project_id: str) -> str:
    """Return the next sequential decision ID for this project."""
    _decision_counters[project_id] = _decision_counters.get(project_id, 0) + 1
    return make_decision_id(project_id, _decision_counters[project_id])


def next_outcome_id(project_id: str) -> str:
    """Return the next sequential outcome ID for this project."""
    _outcome_counters[project_id] = _outcome_counters.get(project_id, 0) + 1
    return make_outcome_id(project_id, _outcome_counters[project_id])


def reset_counters_for_testing() -> None:
    """
    Reset all counters. Call only from test teardown — never from production code.
    """
    _decision_counters.clear()
    _outcome_counters.clear()
