"""Timeline page — Chronological evolution and supersession of architectural decisions."""

from __future__ import annotations

import streamlit as st

from contracts import DecisionFilter
from contracts.errors import ScopeError
from ui.adapters import get_backend
from ui.components._theme import inject_custom_css
from ui.components.dialogs import check_and_render_evidence_dialog
from ui.components.renders import render_decision_card, render_decision_timeline

backend = get_backend()
role = st.session_state.get("role") or "admin"

inject_custom_css()
check_and_render_evidence_dialog(backend, role)

st.title("📅 Architectural Decision Timeline")
st.markdown(
    "<p style='color:#94A3B8; font-size:1.05rem;'>Trace how architectural decisions evolve from original ADRs through recurring exceptions, incident postmortems, and eventual supersession.</p>",
    unsafe_allow_html=True,
)

# 1. Decision Selector
try:
    all_decisions = backend.search_decisions(DecisionFilter(), role)
    dec_options = [f"{d.decision_id}: {d.title}" for d in all_decisions]
    id_map = {f"{d.decision_id}: {d.title}": d.decision_id for d in all_decisions}
except Exception as e:  # noqa: BLE001
    st.error(f"Failed to fetch decisions: {e}")
    dec_options = ["DEC-ALPHA-001: Reject Kafka for messaging"]
    id_map = {"DEC-ALPHA-001: Reject Kafka for messaging": "DEC-ALPHA-001"}

# Check if pre-selected from another page
preselected = st.session_state.get("selected_decision_id") or "DEC-ALPHA-001"
default_idx = 0
for i, opt in enumerate(dec_options):
    if preselected and preselected in opt:
        default_idx = i
        break

selected_option = st.selectbox("Select Decision to Trace", dec_options, index=default_idx)
selected_did = id_map.get(selected_option, "DEC-ALPHA-001")

st.markdown("---")

# 2. Decision Details & Timeline
try:
    decision = backend.get_decision(selected_did, role)
    events = backend.get_decision_timeline(selected_did, role)

    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("### Decision Baseline")
        render_decision_card(decision)
    with col2:
        render_decision_timeline(events)

except ScopeError as se:
    st.warning(f"🔒 {se}")
except Exception as e:  # noqa: BLE001
    st.error(f"Could not load timeline for {selected_did}: {e}")
