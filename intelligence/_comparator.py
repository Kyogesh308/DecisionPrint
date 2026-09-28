"""
intelligence/_comparator.py

Builds the comparator text block: a structured markdown summary of a Decision's
historical constraints vs current project constraints, including drift results.
"""

from __future__ import annotations

import logging

from contracts.enums import ConstraintComparison, DriftLevel
from contracts.models import Decision, DriftResult

logger = logging.getLogger("decisionprint.intelligence.comparator")

_COMPARISON_EMOJI = {
    ConstraintComparison.SAME: "✓ same",
    ConstraintComparison.CHANGED: "⚡ changed",
    ConstraintComparison.UNKNOWN: "? unknown (absent from current context)",
    ConstraintComparison.NEWLY_PRESENT: "＋ new (not in historical decision)",
    ConstraintComparison.INCOMPARABLE: "~ incomparable (type mismatch or null)",
}

_DRIFT_LEVEL_TEXT = {
    DriftLevel.NONE: "No meaningful drift detected.",
    DriftLevel.LOW: "Low drift — context has shifted slightly.",
    DriftLevel.MEDIUM: "Medium drift — several decision premises have changed.",
    DriftLevel.HIGH: "High drift — the foundational constraints of this decision have materially changed.",
}


def build_comparator_text(
    *,
    decision: Decision,
    drift_result: DriftResult,
    query: str,
) -> str:
    lines: list[str] = []

    lines.append(f"## Historical Decision: {decision.title}")
    lines.append(f"**Decision ID:** {decision.id}")
    lines.append(f"**Project:** {decision.project_id}")
    lines.append(f"**Occurred:** {decision.occurred_at}")
    lines.append(f"**Selected option:** {decision.selected_option}")
    lines.append("")

    lines.append("### Decision Statement")
    lines.append(decision.decision_statement)
    lines.append("")

    if decision.reasons:
        lines.append("### Original Reasons")
        for r in decision.reasons:
            source = f" _(source: {r.source_memory_id})_" if r.source_memory_id else ""
            lines.append(f"- {r.statement}{source}")
        lines.append("")

    lines.append("### Constraint Comparison")
    lines.append("")
    lines.append("| Constraint | Historical | Current | Status | Reason-Linked |")
    lines.append("|---|---|---|---|---|")

    for item in drift_result.delta.items:
        hist = _format_value(item.historical_value)
        curr = _format_value(item.current_value)
        status = _COMPARISON_EMOJI.get(item.comparison, str(item.comparison))
        reason_flag = "✓" if item.is_reason_linked else ""
        lines.append(f"| `{item.key}` | {hist} | {curr} | {status} | {reason_flag} |")

    lines.append("")

    lines.append("### Drift Summary")
    drift_text = _DRIFT_LEVEL_TEXT.get(drift_result.level, "")
    lines.append(f"**Drift level:** {drift_result.level.value.upper()} — {drift_text}")
    lines.append(f"**Drift score:** {drift_result.score:.2f}")
    lines.append(f"**Drift confidence:** {drift_result.drift_confidence:.2f}")
    lines.append(
        f"**Reconsideration warranted:** {'YES' if drift_result.reconsideration_warranted else 'NO'}"
    )
    lines.append("")

    changed_reason_linked = [
        i
        for i in drift_result.delta.items
        if i.is_reason_linked and i.comparison == ConstraintComparison.CHANGED
    ]
    if changed_reason_linked:
        lines.append("### Changed Foundational Premises")
        lines.append(
            "The following constraints were **reason-linked** in the original decision "
            "and have materially changed:"
        )
        for item in changed_reason_linked:
            lines.append(
                f"- **`{item.key}`**: was `{_format_value(item.historical_value)}`, "
                f"now `{_format_value(item.current_value)}`"
                + (f" — {item.note}" if item.note else "")
            )
        lines.append("")

    unchanged_reason_linked = [
        i
        for i in drift_result.delta.items
        if i.is_reason_linked and i.comparison == ConstraintComparison.SAME
    ]
    if unchanged_reason_linked:
        lines.append("### Unchanged Foundational Premises")
        for item in unchanged_reason_linked:
            lines.append(
                f"- **`{item.key}`**: still `{_format_value(item.current_value)}`"
            )
        lines.append("")

    if decision.alternatives:
        lines.append("### Historical Alternatives Considered")
        for alt in decision.alternatives:
            lines.append(f"- **{alt.option}** ({alt.disposition}): {alt.reason}")
        lines.append("")

    lines.append("### Query Being Answered")
    lines.append(f"> {query}")
    lines.append("")

    return "\n".join(lines)


def build_multi_decision_comparator(
    *,
    decisions_and_drift: list[tuple[Decision, DriftResult]],
    query: str,
) -> str:
    sorted_pairs = sorted(decisions_and_drift, key=lambda p: p[1].score, reverse=True)
    blocks = [
        build_comparator_text(decision=d, drift_result=dr, query=query)
        for d, dr in sorted_pairs
    ]
    separator = "\n\n---\n\n"
    return separator.join(blocks)


def _format_value(v: object) -> str:
    if v is None:
        return "—"
    if isinstance(v, bool):
        return "true" if v else "false"
    return str(v)
