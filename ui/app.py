"""Main entry point for DecisionPrint UI."""

from __future__ import annotations

import os

import streamlit as st
from dotenv import load_dotenv

from ui.components._state import init_session_state
from ui.components._theme import inject_custom_css

st.set_page_config(page_title="DecisionPrint", page_icon="🧠", layout="wide")
load_dotenv()


def render_sidebar() -> None:
    """Render the sidebar with logo, role switcher, and badges."""
    st.sidebar.markdown("<h1 class='dp-sidebar-logo'>🧠 DecisionPrint</h1>", unsafe_allow_html=True)
    st.sidebar.markdown("<p class='dp-sidebar-sub'>Organizational Decision Memory</p>", unsafe_allow_html=True)
    st.sidebar.markdown("---")

    st.sidebar.selectbox("Role", ["engineer", "project_lead", "executive", "admin"], key="role")

    backend = os.getenv("DP_BACKEND", "fixture")
    badge_color = "#4ade80" if backend == "fixture" else "#60a5fa"
    st.sidebar.markdown(
        f"<div class='dp-backend-badge' style='border-color:{badge_color};color:{badge_color}'>Backend: {backend.upper()}</div>",
        unsafe_allow_html=True,
    )

    st.sidebar.markdown("<div class='dp-version'>v3.0.0-alpha</div>", unsafe_allow_html=True)


def render_main() -> None:
    """Render the executive launchpad and feature showcase."""
    st.markdown(
        """
    <div class='dp-hero'>
        <h1>🧠 DecisionPrint</h1>
        <p class='dp-hero-sub'>The living memory of your organization's architectural and engineering decisions.</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    from ui.adapters import get_backend

    role = st.session_state.get("role", "admin")
    backend = get_backend()
    try:
        overview = backend.get_memory_overview(role)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Historical Projects", overview.project_count)
        c2.metric("Grounded Sources", overview.source_count)
        c3.metric("Indexed Decisions", overview.decision_count)
        c4.metric("Consolidated Models", overview.mental_model_count)
    except Exception:  # noqa: BLE001, S110
        pass

    st.markdown("---")
    st.markdown("### 🚀 Core Platform Capabilities")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            """
        <div class='dp-card'>
            <h4>🔍 1. Continuous Memory Recall (The Ask Screen)</h4>
            <p style='color:#94A3B8;'>Evaluate new proposals (e.g. <em>"Should Nova use Kafka?"</em>) against historical precedents, automatic constraint deltas, and multi-dimensional confidence scores.</p>
        </div>
        """,
            unsafe_allow_html=True,
        )
        if st.button("Open Ask Screen ➔", key="nav_ask"):
            st.switch_page("pages/1_Ask.py")

        st.markdown(
            """
        <div class='dp-card'>
            <h4>📊 0. Memory Overview & Ingestion</h4>
            <p style='color:#94A3B8;'>Explore high-level organizational memory statistics, full-text decision search, and live document ingestion with real-time memory consolidation.</p>
        </div>
        """,
            unsafe_allow_html=True,
        )
        if st.button("Open Memory Overview ➔", key="nav_overview"):
            st.switch_page("pages/0_Overview.py")

        st.markdown(
            """
        <div class='dp-card'>
            <h4>🏗️ 2. Current Projects & Decision Drift</h4>
            <p style='color:#94A3B8;'>Monitor active project constraints and audit decision drift warnings when original operational premises no longer hold.</p>
        </div>
        """,
            unsafe_allow_html=True,
        )
        if st.button("Open Current Projects ➔", key="nav_proj"):
            st.switch_page("pages/2_Current_Projects.py")

    with col2:
        st.markdown(
            """
        <div class='dp-card'>
            <h4>🔗 6. Outcome Chain & Causal Links</h4>
            <p style='color:#94A3B8;'>Trace how cost-cutting directives in Project Delta caused a production outage, backed by postmortem evidence with an <strong>EXPLICIT CAUSAL LINK</strong>.</p>
        </div>
        """,
            unsafe_allow_html=True,
        )
        if st.button("Open Outcome Chain ➔", key="nav_chain"):
            st.switch_page("pages/6_Outcome_Chain.py")

        st.markdown(
            """
        <div class='dp-card'>
            <h4>📅 3. Decision Timeline & Supersession</h4>
            <p style='color:#94A3B8;'>Inspect how decisions evolve across project iterations: from initial ADRs through recurring exceptions to formal supersession.</p>
        </div>
        """,
            unsafe_allow_html=True,
        )
        if st.button("Open Timeline ➔", key="nav_timeline"):
            st.switch_page("pages/3_Timeline.py")

        st.markdown(
            """
        <div class='dp-card'>
            <h4>🧬 5. Memory Evolution & Mental Models</h4>
            <p style='color:#94A3B8;'>Watch raw project decisions consolidate into recurring architectural observations and company-wide mental models.</p>
        </div>
        """,
            unsafe_allow_html=True,
        )
        if st.button("Open Memory Evolution ➔", key="nav_evolution"):
            st.switch_page("pages/5_Memory_Evolution.py")


def main() -> None:
    """Run the Streamlit application."""
    init_session_state()
    inject_custom_css()
    render_sidebar()
    render_main()


if __name__ == "__main__":
    main()
