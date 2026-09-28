"""UI rendering components and shell."""

from __future__ import annotations

from ui.components._theme import badge_html, inject_custom_css, inject_theme
from ui.components._viz import (
    render_drift_gauge,
    render_stat_tile,
    render_traceability_meter,
)
from ui.components.icons import get_icon_svg
from ui.components.renders import (
    render_brief,
    render_confidence_breakdown,
    render_constraint_delta_table,
    render_decision_card,
    render_decision_detail_panel,
    render_decision_timeline,
    render_drift_alert_summary,
    render_drift_card,
    render_epistemic_section,
    render_evidence_panel,
    render_ingest_result,
    render_memory_overview,
    render_memory_trace_drawer,
    render_mental_model_card,
    render_mental_models_grid,
    render_observation_card,
    render_outcome_chain,
    render_recent_activity,
    render_suggested_queries,
    render_system_health,
)
from ui.components.shell import get_nav_badges, render_nav_context_bar, render_sidebar_chrome, render_top_bar

__all__ = [
    "badge_html",
    "get_icon_svg",
    "get_nav_badges",
    "inject_custom_css",
    "inject_theme",
    "render_brief",
    "render_confidence_breakdown",
    "render_constraint_delta_table",
    "render_decision_card",
    "render_decision_detail_panel",
    "render_decision_timeline",
    "render_drift_alert_summary",
    "render_drift_card",
    "render_drift_gauge",
    "render_epistemic_section",
    "render_evidence_panel",
    "render_ingest_result",
    "render_memory_overview",
    "render_memory_trace_drawer",
    "render_mental_model_card",
    "render_mental_models_grid",
    "render_nav_context_bar",
    "render_observation_card",
    "render_outcome_chain",
    "render_recent_activity",
    "render_sidebar_chrome",
    "render_stat_tile",
    "render_suggested_queries",
    "render_system_health",
    "render_top_bar",
    "render_traceability_meter",
]
