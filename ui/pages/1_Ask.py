"""Ask page — The core DecisionPrint intelligence interface matching Screen 2."""

from __future__ import annotations

import streamlit as st

from ui.adapters import get_backend
from ui.components import (
    inject_custom_css,
    render_brief,
    render_sidebar_chrome,
    render_top_bar,
)
from ui.components.dialogs import check_and_render_evidence_dialog, show_memory_trace_dialog

inject_custom_css()

backend = get_backend()
role = st.session_state.get("role") or "admin"

render_top_bar(active_stage="ANALYZE")
render_sidebar_chrome()
check_and_render_evidence_dialog(backend, role)

# 1. Page Header
st.markdown(
    """
    <div style='margin-bottom: 1.5rem;'>
        <h1 style='margin-bottom: 0.25rem;'>Ask DecisionPrint</h1>
        <p style='color:#94A3B8; font-size:1.02rem; margin:0;'>
            Query your organizational memory to detect architectural drift, validate constraints, and ground technical choices in historical outcomes.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# 2. Query Composer Card
st.markdown("<div class='dp-card'>", unsafe_allow_html=True)
st.markdown(
    "<div style='font-size:0.9rem; font-weight:600; color:#F8FAFC; margin-bottom:0.5rem;'>Ask a question</div>",
    unsafe_allow_html=True,
)

try:
    projects = backend.list_projects(role)
    p_ids = [p.project_id for p in projects]
except Exception:  # noqa: BLE001
    p_ids = ["nova", "alpha", "beta", "gamma", "delta"]

col_proj, col_input, col_btn = st.columns([1.2, 4, 1])
with col_proj:
    selected_project = st.selectbox(
        "Project Context",
        p_ids,
        index=p_ids.index("nova") if "nova" in p_ids else 0,
        label_visibility="collapsed",
    )

with col_input:
    current_q = st.session_state.get("ask_input", "Should Nova use Kafka for event streaming?")
    question = st.text_input(
        "Ask a decision question",
        value=current_q,
        placeholder="Should Nova use Kafka for event streaming?",
        label_visibility="collapsed",
    )

with col_btn:
    do_ask = st.button("🔍 Search", type="primary", use_container_width=True)

# Suggested Questions Row
st.markdown(
    "<div style='font-size:0.78rem; color:#94A3B8; font-weight:600; margin-top:0.8rem;'>Suggested questions:</div>",
    unsafe_allow_html=True,
)
sq_cols = st.columns(4)
if sq_cols[0].button("Why reject GraphQL?", key="sq_graphql"):
    st.session_state.ask_input = "Why was GraphQL rejected for internal APIs?"
    st.rerun()
if sq_cols[1].button("Should we use Kafka?", key="sq_kafka"):
    st.session_state.ask_input = "Should Nova use Kafka for event streaming?"
    st.rerun()
if sq_cols[2].button("What were the outcomes?", key="sq_outcomes"):
    st.session_state.ask_input = "What downstream outcomes occurred from backup removal?"
    st.rerun()
if sq_cols[3].button("Why scale Redis?", key="sq_redis"):
    st.session_state.ask_input = "Why did Project Gamma scale Redis to cluster?"
    st.rerun()

st.markdown("</div>", unsafe_allow_html=True)

# Execute query or retrieve cached brief
brief = st.session_state.get("last_brief")

if do_ask or brief is None:
    with st.spinner("Recalling historical decisions, checking premise deltas, and evaluating drift..."):
        try:
            brief = backend.ask_question(question, selected_project, role)
            st.session_state.last_brief = brief
            st.session_state.last_query_id = brief.query_id
        except Exception as e:  # noqa: BLE001
            st.error(f"Error querying memory: {e}")
            brief = None

if brief:
    # Action bar with Memory Trace inspection
    c_left, c_right = st.columns([3, 1])
    with c_left:
        st.markdown(
            f"<div style='font-size:0.82rem; color:#94A3B8; margin-bottom:0.5rem;'>"
            f"Query ID: <code style='color:#818CF8;'>{brief.query_id}</code> &middot; Evaluated under role: <strong>{role}</strong>"
            f"</div>",
            unsafe_allow_html=True,
        )
    with c_right:
        if st.button("🧬 Inspect Memory Trace", key="btn_trace", use_container_width=True):
            try:
                trace = backend.get_memory_trace(brief.query_id, role)
                show_memory_trace_dialog(trace)
            except Exception as e:  # noqa: BLE001
                st.error(f"Could not load memory trace: {e}")

    # Render master Decision Brief
    render_brief(brief)
