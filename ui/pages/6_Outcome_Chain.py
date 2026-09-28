"""Outcome Chain page — Trace causal links from decisions to real-world consequences."""

from __future__ import annotations

import streamlit as st

from contracts import DecisionFilter
from contracts.errors import ScopeError
from ui.adapters import get_backend
from ui.components.dialogs import check_and_render_evidence_dialog
from ui.components.renders import render_outcome_chain

backend = get_backend()
role = st.session_state.get("role", "admin")

check_and_render_evidence_dialog(backend, role)

st.title("🔗 Downstream Outcome & Causal Consequence Chain")
st.markdown(
    "<p style='color:#94A3B8; font-size:1.05rem;'>Auditing the long-term ripple effects of architectural decisions: from cost-cutting directives to outages, postmortems, and policy reversals.</p>",
    unsafe_allow_html=True,
)

# 1. Decision Picker (Default to Cedar / Delta decision)
try:
    all_decisions = backend.search_decisions(DecisionFilter(), role)
    options = [f"{d.decision_id}: {d.title}" for d in all_decisions]
    id_map = {f"{d.decision_id}: {d.title}": d.decision_id for d in all_decisions}
except Exception:  # noqa: BLE001
    options = ["DEC-DELTA-001: Remove automated backups", "DEC-ALPHA-001: Reject Kafka for messaging"]
    id_map = {"DEC-DELTA-001: Remove automated backups": "DEC-DELTA-001"}

# Find index of DEC-DELTA-001 (Cedar chain)
default_idx = 0
for idx, opt in enumerate(options):
    if "DEC-DELTA-001" in opt:
        default_idx = idx
        break

selected_opt = st.selectbox("Select Decision to Audit", options, index=default_idx)
selected_did = id_map.get(selected_opt, "DEC-DELTA-001")

st.markdown("---")

# 2. Render Outcome Chain
try:
    chain = backend.get_outcome_chain(selected_did, role)
    render_outcome_chain(chain)

    st.markdown("### 🔍 Causal Audit Explanation")
    if selected_did == "DEC-DELTA-001":
        st.info(
            "💡 **The Cedar Chain:** In Q2 2025, Project Delta disabled automated backups (`SRC-DELTA-001`, `SRC-DELTA-002`) to save $4,200/mo. "
            "On July 22, 2025, a database outage struck (`SRC-DELTA-003`). The incident postmortem explicitly cited `DEC-DELTA-001` as a direct root-cause "
            "contributor to the data loss and extended MTTR, earning an **EXPLICIT CAUSAL LINK** badge rather than speculative correlation."
        )
    else:
        st.info(
            "💡 Downstream consequences are linked using evidence-backed causal inference. When an official postmortem names a decision, "
            "an **EXPLICIT CAUSAL LINK** is formed."
        )

except ScopeError as se:
    st.warning(f"🔒 {se}")
except Exception as e:  # noqa: BLE001
    st.error(f"Failed to load outcome chain for {selected_did}: {e}")
