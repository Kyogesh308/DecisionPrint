"""Memory Evolution page — Higher-order mental models and synthesized observations matching Screen 6."""

from __future__ import annotations

import streamlit as st

from ui.adapters import get_backend
from ui.components import (
    inject_custom_css,
    render_mental_models_grid,
    render_observation_card,
    render_sidebar_chrome,
    render_top_bar,
)
from ui.components._state import init_session_state, run_guarded
from ui.components.dialogs import check_and_render_evidence_dialog

init_session_state()

if not st.session_state.get("_top_nav_active"):
    inject_custom_css()
    render_top_bar(active_stage="LEARN")
    render_sidebar_chrome()

backend = get_backend()
role = st.session_state.get("role") or "admin"
check_and_render_evidence_dialog(backend, role)

# 1. Header
st.markdown(
    """
    <div style='margin-bottom: 1.25rem;'>
        <h1 style='margin-bottom: 0.25rem;'>Memory Evolution</h1>
        <p style='color:var(--dp-text-secondary); font-size:1.02rem; margin:0;'>
            How your organization's architecture decisions, assumptions, and context evolve over time.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# 2. KPI Metrics Row (3 Cards matching Screen 6)
try:
    overview = run_guarded(backend.get_memory_overview, role)
    k1, k2, k3 = st.columns(3)
    with k1:
        st.markdown(
            f"""
        <div class='dp-kpi-card'>
            <div class='dp-kpi-label'>Total Observations</div>
            <div class='dp-kpi-value'>{overview.total_observations}</div>
            <div class='dp-kpi-trend-pos'>+4 this month</div>
        </div>
        """,
            unsafe_allow_html=True,
        )
    with k2:
        st.markdown(
            f"""
        <div class='dp-kpi-card'>
            <div class='dp-kpi-label'>Mental Models</div>
            <div class='dp-kpi-value' style='color:var(--dp-primary);'>{overview.total_mental_models}</div>
            <div class='dp-kpi-trend-pos'>+1 this month</div>
        </div>
        """,
            unsafe_allow_html=True,
        )
    with k3:
        st.markdown(
            f"""
        <div class='dp-kpi-card'>
            <div class='dp-kpi-label'>Total Facts</div>
            <div class='dp-kpi-value' style='color:var(--dp-primary);'>{overview.total_facts}</div>
            <div class='dp-kpi-trend-pos'>+12 this month</div>
        </div>
        """,
            unsafe_allow_html=True,
        )
except Exception as e:  # noqa: BLE001
    st.error(f"Failed to load metrics: {e}")

st.markdown("<div style='height: 1.25rem;'></div>", unsafe_allow_html=True)

# 3. Higher-Order Mental Models Grid matching Screen 6
try:
    models = run_guarded(backend.list_mental_models, role)
    render_mental_models_grid(models)
except Exception as e:  # noqa: BLE001
    st.error(f"Failed to fetch mental models: {e}")

st.markdown("<div style='height: 1.25rem;'></div>", unsafe_allow_html=True)

# 4. Synthesized Observations with Topic Filter
st.markdown("### 🔭 Synthesized Observations & Evolutionary Trajectories")
st.caption(
    "Observations strengthen as evidence repeats across independent project lifecycles. Notice how evidence counts grow over time:"
)

col_topic, col_empty = st.columns([2, 3])
with col_topic:
    topic_choice = st.selectbox(
        "Filter by Topic Area", ["All Topics", "messaging", "cost", "redis", "debugging", "observability"], index=0
    )

topic_arg = None if topic_choice == "All Topics" else topic_choice

try:
    observations = run_guarded(backend.list_observations, role, topic_arg)
    if observations:
        for obs in observations:
            render_observation_card(obs)
    else:
        st.info("🔄 No observations currently match this topic or observations are still consolidating.")
except Exception as e:  # noqa: BLE001
    st.error(f"Failed to fetch observations: {e}")
