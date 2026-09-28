"""Main entry point for DecisionPrint UI — Enterprise Architecture Intelligence Platform."""

from __future__ import annotations

import streamlit as st
from dotenv import load_dotenv

from ui.adapters import get_backend
from ui.components import (
    inject_custom_css,
    render_memory_overview,
    render_sidebar_chrome,
    render_top_bar,
)
from ui.components._state import init_session_state

st.set_page_config(page_title="DecisionPrint", page_icon="🧠", layout="wide")
load_dotenv()


def render_launchpad() -> None:
    """Render the executive launchpad and feature showcase matching the enterprise design."""
    render_top_bar(active_stage="DECIDE")
    render_sidebar_chrome()

    st.markdown(
        """
        <div style='margin-bottom: 1.5rem;'>
            <h1 style='margin-bottom: 0.25rem;'>Good afternoon, John</h1>
            <p style='color:#94A3B8; font-size:1.02rem; margin:0;'>
                Welcome to DecisionPrint — the organizational decision memory and architecture intelligence system.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    role = st.session_state.get("role") or "admin"
    backend = get_backend()
    try:
        overview = backend.get_memory_overview(role)
        render_memory_overview(overview)
    except Exception:  # noqa: BLE001, S110
        pass

    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
    st.markdown("### Core Intelligence Modules")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            """
            <div class='dp-card'>
                <h4>🔍 Continuous Memory Recall (The Ask Screen)</h4>
                <p style='color:#94A3B8; font-size:0.9rem;'>
                    Evaluate technical proposals (e.g. <em>"Should Nova use Kafka?"</em>) against historical precedents,
                    automatic constraint deltas, and multi-dimensional confidence scores.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Open Ask Screen &rarr;", key="launch_ask", use_container_width=True):
            st.switch_page("pages/1_Ask.py")

        st.markdown(
            """
            <div class='dp-card'>
                <h4>📊 Organizational Memory Overview</h4>
                <p style='color:#94A3B8; font-size:0.9rem;'>
                    Explore high-level decision memory statistics, full-text decision search, and live document ingestion with real-time memory consolidation.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Open Memory Overview &rarr;", key="launch_overview", use_container_width=True):
            st.switch_page("pages/0_Overview.py")

        st.markdown(
            """
            <div class='dp-card'>
                <h4>🏗️ Current Projects &amp; Decision Drift</h4>
                <p style='color:#94A3B8; font-size:0.9rem;'>
                    Monitor active project constraints and audit decision drift warnings when original operational premises no longer hold.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Open Current Projects &rarr;", key="launch_proj", use_container_width=True):
            st.switch_page("pages/2_Current_Projects.py")

    with col2:
        st.markdown(
            """
            <div class='dp-card'>
                <h4>🔗 Outcome Chain &amp; Causal Consequence</h4>
                <p style='color:#94A3B8; font-size:0.9rem;'>
                    Trace how cost-cutting directives in Project Delta caused a production outage, backed by postmortem evidence with an <strong>EXPLICIT CAUSAL LINK</strong>.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Open Outcome Chain &rarr;", key="launch_chain", use_container_width=True):
            st.switch_page("pages/6_Outcome_Chain.py")

        st.markdown(
            """
            <div class='dp-card'>
                <h4>📅 Architectural Decision Timeline</h4>
                <p style='color:#94A3B8; font-size:0.9rem;'>
                    Inspect how architectural decisions evolve across project iterations: from initial ADRs through recurring exceptions to formal supersession.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Open Timeline &rarr;", key="launch_timeline", use_container_width=True):
            st.switch_page("pages/3_Timeline.py")

        st.markdown(
            """
            <div class='dp-card'>
                <h4>🧬 Memory Evolution &amp; Mental Models</h4>
                <p style='color:#94A3B8; font-size:0.9rem;'>
                    Watch raw project decisions consolidate into recurring architectural observations and company-wide mental models.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Open Memory Evolution &rarr;", key="launch_evolution", use_container_width=True):
            st.switch_page("pages/5_Memory_Evolution.py")


def main() -> None:
    """Run the Streamlit application."""
    init_session_state()
    inject_custom_css()
    render_launchpad()


if __name__ == "__main__":
    main()
