"""Ask page — The core DecisionPrint intelligence interface."""

from __future__ import annotations

import streamlit as st

from ui.adapters import get_backend
from ui.components.dialogs import check_and_render_evidence_dialog, show_memory_trace_dialog
from ui.components.renders import render_brief

backend = get_backend()
role = st.session_state.get("role", "admin")

# Always check if evidence dialog needs to be opened
check_and_render_evidence_dialog(backend, role)

st.title("🔍 Ask DecisionPrint")
st.markdown(
    "<p style='color:#94A3B8; font-size:1.05rem;'>Query organizational memory to detect architectural drift, invalidate obsolete constraints, and ground technical choices in historical outcomes.</p>",
    unsafe_allow_html=True,
)

# 1. Project Selector & Question Box
c1, c2 = st.columns([1, 3])
with c1:
    try:
        projects = backend.list_projects(role)
        p_ids = [p.project_id for p in projects]
    except Exception:  # noqa: BLE001
        p_ids = ["nova", "alpha", "beta", "gamma", "delta"]
    selected_project = st.selectbox("Current Project", p_ids, index=p_ids.index("nova") if "nova" in p_ids else 0)

with c2:
    question = st.text_input(
        "Ask a decision question",
        value=st.session_state.get("ask_input", "Should Nova use Kafka for event streaming?"),
        placeholder="e.g. Should Nova use Kafka? Why was GraphQL rejected?",
    )

col_ask, col_quick1, col_quick2, col_quick3 = st.columns([1.5, 1.5, 1.5, 1.5])
do_ask = col_ask.button("🧠 Query Memory", type="primary")
if col_quick1.button("Should Nova use Kafka?"):
    st.session_state.ask_input = "Should Nova use Kafka for event streaming?"
    st.rerun()
if col_quick2.button("Why reject GraphQL?"):
    st.session_state.ask_input = "Why was GraphQL rejected?"
    st.rerun()
if col_quick3.button("Why scale Redis?"):
    st.session_state.ask_input = "Has Redis scaling been an issue?"
    st.rerun()

st.markdown("---")

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
    # Top action bar with Memory Trace inspection
    c_left, c_right = st.columns([3, 1])
    with c_left:
        st.caption(f"Query ID: `{brief.query_id}` · Scope evaluated under role: **{role}**")
    with c_right:
        if st.button("🧬 Inspect Memory Trace", key="btn_trace"):
            try:
                trace = backend.get_memory_trace(brief.query_id, role)
                show_memory_trace_dialog(trace)
            except Exception as e:  # noqa: BLE001
                st.error(f"Could not load memory trace: {e}")

    # Render the master Decision Brief above the fold
    render_brief(brief)
