"""Timeline page — Chronological view of architectural decisions and key events matching Screen 4."""

from __future__ import annotations

import streamlit as st

from contracts import DecisionFilter
from ui.adapters import get_backend
from ui.components import (
    inject_custom_css,
    render_decision_card,
    render_decision_detail_panel,
    render_decision_timeline,
    render_sidebar_chrome,
    render_top_bar,
)
from ui.components._state import init_session_state, run_guarded
from ui.components.dialogs import check_and_render_evidence_dialog

init_session_state()

if not st.session_state.get("_top_nav_active"):
    inject_custom_css()
    render_top_bar(active_stage="DECIDE")
    render_sidebar_chrome()

backend = get_backend()
role = st.session_state.get("role") or "admin"

check_and_render_evidence_dialog(backend, role)

# 1. Header with View Toggle
c_head, c_toggle = st.columns([4, 1])
with c_head:
    st.markdown(
        """
        <div style='margin-bottom: 1.25rem;'>
            <h1 style='margin-bottom: 0.25rem;'>Decision Timeline</h1>
            <p style='color:var(--dp-text-secondary); font-size:1.02rem; margin:0;'>
                Chronological view of architectural decisions, lifecycle milestones, and key evolution events.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
with c_toggle:
    view_mode = st.radio("View", ["Timeline", "List"], horizontal=True, label_visibility="collapsed")

# 2. Decision Selector
all_decisions = run_guarded(lambda: backend.search_decisions(DecisionFilter(), role))
if all_decisions:
    dec_options = [f"{d.decision_id}: {d.title}" for d in all_decisions]
    id_map = {f"{d.decision_id}: {d.title}": d.decision_id for d in all_decisions}
else:
    dec_options = ["DEC-ALPHA-001: Reject Kafka for messaging"]
    id_map = {"DEC-ALPHA-001: Reject Kafka for messaging": "DEC-ALPHA-001"}

preselected = st.session_state.get("selected_decision_id")
default_idx = 0
if preselected:
    for i, opt in enumerate(dec_options):
        if preselected in opt:
            default_idx = i
            break

selected_option = st.selectbox("Select Decision Lifecycle to Audit", dec_options, index=default_idx)
selected_did = id_map.get(selected_option, "DEC-ALPHA-001")

st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

# 3. Decision Timeline & Detail Panel
decision = run_guarded(lambda: backend.get_decision(selected_did, role))
events = run_guarded(lambda: backend.get_decision_timeline(selected_did, role))

if decision and events is not None:
    if view_mode == "Timeline":
        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown("### Chronological Evolution")
            render_decision_timeline(events)
        with col2:
            st.markdown("### Selected Decision Baseline")
            render_decision_card(decision)
    else:
        st.markdown("### Decision Milestones List")
        for ev in events:
            st.markdown(
                f"""
            <div class='dp-card' style='padding:0.9rem 1.2rem; margin-bottom:0.6rem; border-left: 3px solid var(--dp-primary);'>
                <div style='display:flex; justify-content:space-between; align-items:center;'>
                    <strong>{ev.title}</strong>
                    <span style='font-size:0.75rem; color:var(--dp-primary); font-family:"JetBrains Mono", monospace;'>{ev.occurred_at.strftime("%b %d, %Y")}</span>
                </div>
                <div style='font-size:0.85rem; color:var(--dp-text-secondary); margin-top:0.3rem;'>{ev.summary}</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

    # Bottom Decision Detail Panel matching Mockup Screen 4
    render_decision_detail_panel(decision)
