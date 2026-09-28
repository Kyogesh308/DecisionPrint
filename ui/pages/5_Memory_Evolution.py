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
from ui.components.dialogs import check_and_render_evidence_dialog

inject_custom_css()

backend = get_backend()
role = st.session_state.get("role") or "admin"

render_top_bar(active_stage="LEARN")
render_sidebar_chrome()
check_and_render_evidence_dialog(backend, role)

# 1. Header
st.markdown(
    """
    <div style='margin-bottom: 1.25rem;'>
        <h1 style='margin-bottom: 0.25rem;'>Memory Evolution</h1>
        <p style='color:#94A3B8; font-size:1.02rem; margin:0;'>
            How your organization's architecture decisions, assumptions, and context evolve over time.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# 2. KPI Metrics Row (3 Cards matching Screen 6)
k1, k2, k3 = st.columns(3)
with k1:
    st.markdown(
        """
    <div class='dp-kpi-card'>
        <div class='dp-kpi-label'>Total Memories</div>
        <div class='dp-kpi-value'>12</div>
        <div class='dp-kpi-trend-pos'>+4 this month</div>
    </div>
    """,
        unsafe_allow_html=True,
    )
with k2:
    st.markdown(
        """
    <div class='dp-kpi-card'>
        <div class='dp-kpi-label'>Mental Models</div>
        <div class='dp-kpi-value' style='color:#818CF8;'>3</div>
        <div class='dp-kpi-trend-pos'>+1 this month</div>
    </div>
    """,
        unsafe_allow_html=True,
    )
with k3:
    st.markdown(
        """
    <div class='dp-kpi-card'>
        <div class='dp-kpi-label'>Evidence Items</div>
        <div class='dp-kpi-value' style='color:#38BDF8;'>48</div>
        <div class='dp-kpi-trend-pos'>+12 this month</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

st.markdown("<div style='height: 1.25rem;'></div>", unsafe_allow_html=True)

# 3. Higher-Order Mental Models Grid matching Screen 6
try:
    models = backend.list_mental_models(role)
    render_mental_models_grid(models)
except Exception as e:  # noqa: BLE001
    st.error(f"Failed to fetch mental models: {e}")

st.markdown("<div style='height: 1.25rem;'></div>", unsafe_allow_html=True)

# 4. Recent Memory Ingestions Table / Feed
st.markdown("<div class='dp-card'>", unsafe_allow_html=True)
st.markdown("### Recent Memory Ingestions")
st.caption("Fresh technical evidence continuously grounded in repository artifacts and transcripts:")

st.markdown(
    """
    <table class='dp-table'>
        <thead>
            <tr>
                <th>Ingested Memory Topic</th>
                <th>Target Project</th>
                <th>Date Grounded</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><strong>Kafka event patterns and throughput benchmarks</strong></td>
                <td><span class='dp-badge' style='background:rgba(99,102,241,0.15); color:#818CF8; border:1px solid rgba(99,102,241,0.3);'>PROJECT NOVA</span></td>
                <td style='font-family:"JetBrains Mono", monospace; font-size:0.82rem; color:#94A3B8;'>May 13, 2026</td>
            </tr>
            <tr>
                <td><strong>PostgreSQL query performance analysis</strong></td>
                <td><span class='dp-badge' style='background:rgba(56,189,248,0.15); color:#38BDF8; border:1px solid rgba(56,189,248,0.3);'>PROJECT HELIOS</span></td>
                <td style='font-family:"JetBrains Mono", monospace; font-size:0.82rem; color:#94A3B8;'>Apr 29, 2026</td>
            </tr>
            <tr>
                <td><strong>Redis caching degradation patterns</strong></td>
                <td><span class='dp-badge' style='background:rgba(249,115,22,0.15); color:#FB923C; border:1px solid rgba(251,146,60,0.3);'>PROJECT ORION</span></td>
                <td style='font-family:"JetBrains Mono", monospace; font-size:0.82rem; color:#94A3B8;'>Feb 18, 2026</td>
            </tr>
        </tbody>
    </table>
    """,
    unsafe_allow_html=True,
)
st.markdown("</div>", unsafe_allow_html=True)

# 5. Synthesized Observations with Topic Filter
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
    observations = backend.list_observations(role, topic_arg)
    if observations:
        for obs in observations:
            render_observation_card(obs)
    else:
        st.info("🔄 No observations currently match this topic or observations are still consolidating.")
except Exception as e:  # noqa: BLE001
    st.error(f"Failed to fetch observations: {e}")
