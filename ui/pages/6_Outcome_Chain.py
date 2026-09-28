"""Outcome Chain page — Trace causal links from decisions to real-world consequences matching Screen 7."""

from __future__ import annotations

import streamlit as st

from contracts import DecisionFilter
from contracts.errors import ScopeError
from ui.adapters import get_backend
from ui.components import (
    badge_html,
    inject_custom_css,
    render_outcome_chain,
    render_sidebar_chrome,
    render_top_bar,
)
from ui.components.dialogs import check_and_render_evidence_dialog

inject_custom_css()

backend = get_backend()
role = st.session_state.get("role") or "admin"

render_top_bar(active_stage="DECIDE")
render_sidebar_chrome()
check_and_render_evidence_dialog(backend, role)

# 1. Header with Project Selector
c_head, c_sel = st.columns([3, 1.5])
with c_head:
    st.markdown(
        """
        <div style='margin-bottom: 1.25rem;'>
            <h1 style='margin-bottom: 0.25rem;'>Outcome Chain</h1>
            <p style='color:#94A3B8; font-size:1.02rem; margin:0;'>
                Trace how cost-cutting directives and architectural choices link directly to project outcomes and evidence.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c_sel:
    # Decision Picker
    try:
        all_decisions = backend.search_decisions(DecisionFilter(), role)
        options = [f"{d.decision_id}: {d.title}" for d in all_decisions]
        id_map = {f"{d.decision_id}: {d.title}": d.decision_id for d in all_decisions}
    except Exception:  # noqa: BLE001
        options = ["DEC-DELTA-001: Remove automated backups", "DEC-ALPHA-001: Reject Kafka for messaging"]
        id_map = {"DEC-DELTA-001: Remove automated backups": "DEC-DELTA-001"}

    preselected = st.session_state.get("selected_decision_id") or "DEC-DELTA-001"
    default_idx = 0
    for idx, opt in enumerate(options):
        if preselected and preselected in opt:
            default_idx = idx
            break

    selected_opt = st.selectbox("Audited Decision", options, index=default_idx)
    selected_did = id_map.get(selected_opt, "DEC-DELTA-001")

st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)

# 2. Render Outcome Chain (Horizontal Visual Flow + Evidence Table)
try:
    chain = backend.get_outcome_chain(selected_did, role)
    render_outcome_chain(chain)

    st.markdown("<div class='dp-card' style='margin-top: 1rem;'>", unsafe_allow_html=True)
    st.markdown("### 🔍 Causal Audit Explanation")
    causal_badge = badge_html("causal", "explicit_causal_link")
    if selected_did == "DEC-DELTA-001":
        st.markdown(
            f"""
            <p style='color:var(--dp-text-primary, #17243B); font-size:0.95rem; line-height: 1.6;'>
                <strong>The Cedar Chain:</strong> In Q2 2025, Project Delta disabled automated database backups
                (<code>SRC-DELTA-001</code>, <code>SRC-DELTA-002</code>) to save $4,200/month under cost-reduction directives.
                On July 22, 2025, an infrastructure outage struck (<code>SRC-DELTA-003</code>). The postmortem explicitly cited
                <code>DEC-DELTA-001</code> as a direct root-cause contributor to data loss and an extended 6-hour MTTR, earning an
                {causal_badge}
                rather than speculative correlation.
            </p>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
            <p style='color:var(--dp-text-primary, #17243B); font-size:0.95rem; line-height: 1.6;'>
                Downstream consequences are audited using evidence-backed causal inference. When an official postmortem names a decision
                or when concrete latency/throughput metrics correlate with an architectural milestone, an
                {causal_badge}
                is formed.
            </p>
            """,
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)

except ScopeError as se:
    st.warning(f"🔒 {se}")
except Exception as e:  # noqa: BLE001
    st.error(f"Failed to load outcome chain for {selected_did}: {e}")
