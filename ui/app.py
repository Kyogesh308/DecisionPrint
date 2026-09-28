"""Main entry point for DecisionPrint UI."""

import os

import streamlit as st
from dotenv import load_dotenv

from ui.components._state import init_session_state

st.set_page_config(page_title="DecisionPrint", page_icon="🧠", layout="wide")
load_dotenv()


def inject_custom_css() -> None:
    """Inject premium dark theme CSS into Streamlit."""
    st.markdown(
        """
<style>
/* =========================================================
   DECISIONPRINT PREMIUM DARK THEME
========================================================= */

/* App Background & Base Typography */
.stApp {
    background-color: #0E1117;
    color: #F8FAFC;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}

/* Base Headings */
h1, h2, h3, h4, h5, h6 {
    color: #F8FAFC !important;
    font-weight: 600 !important;
}

/* Custom Scrollbar */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}
::-webkit-scrollbar-track {
    background: #0E1117; 
}
::-webkit-scrollbar-thumb {
    background: #2D3348; 
    border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
    background: #6C63FF; 
}

/* =========================================================
   SIDEBAR (Glass-morphism)
========================================================= */
[data-testid="stSidebar"] {
    background-color: rgba(26, 31, 46, 0.6) !important;
    backdrop-filter: blur(12px) !important;
    -webkit-backdrop-filter: blur(12px) !important;
    border-right: 1px solid rgba(45, 51, 72, 0.5);
}

.dp-sidebar-logo {
    font-size: 1.75rem !important;
    font-weight: 800 !important;
    background: linear-gradient(to right, #6C63FF, #B06AB3);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0 !important;
    padding-bottom: 0 !important;
}

.dp-sidebar-sub {
    font-size: 0.85rem;
    color: #94A3B8;
    margin-top: 0 !important;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.dp-backend-badge {
    margin-top: 2rem;
    padding: 0.5rem;
    border: 1px solid;
    border-radius: 8px;
    text-align: center;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    background: rgba(26, 31, 46, 0.5);
}

.dp-version {
    margin-top: 1rem;
    text-align: center;
    font-size: 0.75rem;
    color: #475569;
}

/* =========================================================
   MAIN HERO & HEADERS
========================================================= */
.dp-hero {
    background: linear-gradient(135deg, rgba(108, 99, 255, 0.1) 0%, rgba(176, 106, 179, 0.1) 100%);
    padding: 3rem 2rem;
    border-radius: 16px;
    border: 1px solid rgba(108, 99, 255, 0.2);
    text-align: center;
    margin-bottom: 2rem;
    box-shadow: 0 10px 30px -10px rgba(108, 99, 255, 0.15);
    position: relative;
    overflow: hidden;
}

.dp-hero::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(176, 106, 179, 0.05) 0%, transparent 50%);
    animation: rotate 20s linear infinite;
    pointer-events: none;
}

@keyframes rotate {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

.dp-hero h1 {
    font-size: 3.5rem !important;
    background: linear-gradient(to right, #6C63FF, #B06AB3);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.5rem !important;
}

.dp-hero-sub {
    font-size: 1.2rem;
    color: #CBD5E1;
    max-width: 600px;
    margin: 0 auto;
}

/* =========================================================
   CARDS & CONTAINERS
========================================================= */
.dp-card {
    background-color: #1A1F2E;
    border: 1px solid #2D3348;
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    margin-bottom: 1rem;
}

.dp-card:hover {
    border-color: #6C63FF;
    box-shadow: 0 8px 20px -5px rgba(108, 99, 255, 0.15);
    transform: translateY(-2px);
}

/* =========================================================
   INPUTS & CONTROLS
========================================================= */
.stTextInput input, .stTextArea textarea, .stSelectbox > div > div {
    background-color: #1A1F2E !important;
    border: 1px solid #2D3348 !important;
    color: #F8FAFC !important;
    border-radius: 8px !important;
    transition: all 0.2s ease !important;
}

.stTextInput input:focus, .stTextArea textarea:focus, .stSelectbox > div > div:focus {
    border-color: #6C63FF !important;
    box-shadow: 0 0 0 2px rgba(108, 99, 255, 0.2) !important;
}

/* =========================================================
   BUTTONS
========================================================= */
.stButton > button {
    background: linear-gradient(135deg, #6C63FF, #B06AB3) !important;
    border: none !important;
    color: white !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    padding: 0.5rem 1rem !important;
    transition: all 0.3s ease !important;
}

.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(108, 99, 255, 0.4) !important;
    opacity: 0.9 !important;
}

/* Secondary Button (Default Streamlit uses standard style) */
.stButton > button[kind="secondary"] {
    background: #1A1F2E !important;
    border: 1px solid #2D3348 !important;
    color: #E2E8F0 !important;
}

.stButton > button[kind="secondary"]:hover {
    border-color: #6C63FF !important;
    color: #6C63FF !important;
    box-shadow: none !important;
}

/* =========================================================
   METRICS
========================================================= */
[data-testid="stMetricValue"] {
    background: linear-gradient(to right, #60a5fa, #a78bfa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 2.5rem !important;
    font-weight: 700 !important;
}
[data-testid="stMetricLabel"] {
    color: #94A3B8 !important;
    font-size: 1rem !important;
    font-weight: 500 !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* =========================================================
   TABS & EXPANDERS
========================================================= */
.stTabs [data-baseweb="tab-list"] {
    background-color: transparent !important;
    border-bottom: 1px solid #2D3348 !important;
}
.stTabs [data-baseweb="tab"] {
    color: #94A3B8 !important;
    font-weight: 600 !important;
}
.stTabs [aria-selected="true"] {
    color: #B06AB3 !important;
}

[data-testid="stExpander"] {
    background-color: #1A1F2E !important;
    border: 1px solid #2D3348 !important;
    border-radius: 8px !important;
}
[data-testid="stExpander"] summary {
    font-weight: 600 !important;
    color: #F8FAFC !important;
}
[data-testid="stExpander"]:hover {
    border-color: #475569 !important;
}

/* =========================================================
   SPINNERS, DIALOGS, STATUS
========================================================= */
.stSpinner > div > div {
    border-top-color: #6C63FF !important;
}
[data-testid="stDialog"] > div {
    background-color: #1A1F2E !important;
    border: 1px solid #2D3348 !important;
    border-radius: 12px !important;
    box-shadow: 0 20px 40px -10px rgba(0,0,0,0.5) !important;
}

/* Alerts / Callouts */
.stAlert {
    background-color: rgba(30, 58, 95, 0.2) !important;
    border: 1px solid #1e3a5f !important;
    color: #E2E8F0 !important;
    border-radius: 8px !important;
}
[data-testid="stAlert"] svg {
    fill: #60a5fa !important;
}

/* =========================================================
   BADGES & CUSTOM UI ELEMENTS
========================================================= */
.dp-badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}

/* Needs review pulse */
@keyframes pulse-amber {
    0% { box-shadow: 0 0 0 0 rgba(251, 191, 36, 0.4); }
    70% { box-shadow: 0 0 0 6px rgba(251, 191, 36, 0); }
    100% { box-shadow: 0 0 0 0 rgba(251, 191, 36, 0); }
}
.dp-badge-review {
    background: #3d2e1a;
    color: #fbbf24;
    animation: pulse-amber 2s infinite;
}

/* =========================================================
   TIMELINE & OUTCOME CHAIN
========================================================= */
.dp-timeline-item {
    position: relative;
    padding-left: 24px;
    margin-bottom: 24px;
    border-left: 2px solid #2D3348;
}
.dp-timeline-dot {
    position: absolute;
    left: -6px;
    top: 4px;
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background-color: #6C63FF;
    box-shadow: 0 0 8px #6C63FF;
}
.dp-timeline-date {
    font-size: 0.8rem;
    color: #94A3B8;
    margin-bottom: 4px;
}
.dp-chain-link {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin: 1rem 0;
}
.dp-chain-arrow {
    width: 2px;
    height: 30px;
    background: linear-gradient(to bottom, #6C63FF, transparent);
    position: relative;
}
.dp-chain-arrow::after {
    content: '';
    position: absolute;
    bottom: -5px;
    left: -4px;
    border-width: 5px 5px 0 5px;
    border-style: solid;
    border-color: #6C63FF transparent transparent transparent;
}
</style>
    """,
        unsafe_allow_html=True,
    )


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
