"""Current Projects page — Project contexts, constraint editing, and active drift cards."""

from __future__ import annotations

from datetime import UTC, datetime

import streamlit as st

from contracts import CurrentProjectContext
from contracts.errors import ScopeError
from ui.adapters import get_backend
from ui.components.dialogs import check_and_render_evidence_dialog
from ui.components.renders import render_drift_card

backend = get_backend()
role = st.session_state.get("role", "admin")

check_and_render_evidence_dialog(backend, role)

st.title("🏗️ Current Projects & Active Decision Drift")
st.markdown(
    "<p style='color:#94A3B8; font-size:1.05rem;'>Maintain active project context constraints and monitor real-time architectural drift across all technical choices.</p>",
    unsafe_allow_html=True,
)

# 1. Project Selection
try:
    all_projects = backend.list_projects(role)
    proj_map = {p.project_id: p for p in all_projects}
    proj_options = list(proj_map.keys())
except Exception as e:  # noqa: BLE001
    st.error(f"Failed to fetch projects: {e}")
    proj_options = ["nova"]
    proj_map = {}

selected_pid = st.selectbox("Select Project to Inspect", proj_options, index=0)

try:
    context = backend.get_project_context(selected_pid, role)
except ScopeError as se:
    st.warning(f"🔒 {se}")
    st.stop()
except Exception as e:  # noqa: BLE001
    st.error(f"Could not load context for {selected_pid}: {e}")
    st.stop()

# 2. Project Header and Active Drift Cards (addresses G1)
st.markdown(f"### Active Drift Cards for `{context.project_name}`")
try:
    drift_cards = backend.list_drift_cards(selected_pid, role)
    if drift_cards:
        for card in drift_cards:
            render_drift_card(card)
    else:
        st.info("No active decision drift recorded for this project.")
except Exception as e:  # noqa: BLE001
    st.error(f"Could not load drift cards: {e}")

st.markdown("---")

# 3. Context Constraints & Live Edit Form
st.markdown("### ⚙️ Contextual Constraints Configuration")
st.caption(
    "These constraints represent the ground truth operational parameters against which historical decisions are evaluated."
)

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("<div class='dp-card'>", unsafe_allow_html=True)
    st.markdown(f"**Current Constraints for {context.project_name}:**")
    for k, v in context.constraints.items():
        st.markdown(f"- <code>{k}</code> = **{v}**", unsafe_allow_html=True)
    if context.updated_at:
        st.caption(f"Last updated: {context.updated_at.strftime('%Y-%m-%d %H:%M')}")
    st.markdown("</div>", unsafe_allow_html=True)

with col2, st.expander("✏️ Edit Constraints", expanded=False):
    st.markdown("**Update or add a constraint:**")
    key_name = st.text_input("Constraint Key", placeholder="e.g. consumer_count, ops_capacity")
    key_val = st.text_input("New Value", placeholder="e.g. 20, high, small")

    if st.button("Save Constraint Update", type="primary"):
        if key_name and key_val:
            updated_constraints = dict(context.constraints)
            updated_constraints[key_name] = key_val
            updated_context = CurrentProjectContext(
                project_id=context.project_id,
                project_name=context.project_name,
                constraints=updated_constraints,
                updated_at=datetime.now(tz=UTC),
            )
            try:
                backend.update_project_context(updated_context, role)
                st.success(f"Updated `{key_name}` to `{key_val}`!")
                st.rerun()
            except Exception as e:  # noqa: BLE001
                st.error(f"Failed to update context: {e}")
        else:
            st.warning("Please provide both key and value.")
