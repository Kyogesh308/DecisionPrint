"""Current Projects page — Project contexts, constraint auditing, and active drift cards matching Screen 3."""

from __future__ import annotations

from datetime import UTC, datetime

import streamlit as st

from contracts import CurrentProjectContext
from contracts.errors import ScopeError
from ui.adapters import get_backend
from ui.components import (
    inject_custom_css,
    render_drift_card,
    render_sidebar_chrome,
    render_top_bar,
)
from ui.components.dialogs import check_and_render_evidence_dialog

inject_custom_css()

backend = get_backend()
role = st.session_state.get("role") or "admin"

render_top_bar(active_stage="ANALYZE")
render_sidebar_chrome()
check_and_render_evidence_dialog(backend, role)

# 1. Header with New Project CTA
c_title, c_cta = st.columns([4, 1])
with c_title:
    st.markdown(
        """
        <div style='margin-bottom: 1.25rem;'>
            <h1 style='margin-bottom: 0.25rem;'>Current Projects</h1>
            <p style='color:#94A3B8; font-size:1.02rem; margin:0;'>
                Active projects and their decision context, constraints, and architectural drift status.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
with c_cta:
    if st.button("➕ New Project", key="btn_new_project", use_container_width=True):
        st.session_state.show_new_project_modal = True

# 2. KPI Metrics Row (4 Cards)
kp1, kp2, kp3, kp4 = st.columns(4)
with kp1:
    st.markdown(
        """
    <div class='dp-kpi-card'>
        <div class='dp-kpi-label'>Total Projects</div>
        <div class='dp-kpi-value'>5</div>
        <div class='dp-kpi-trend-pos'>Monitored in memory</div>
    </div>
    """,
        unsafe_allow_html=True,
    )
with kp2:
    st.markdown(
        """
    <div class='dp-kpi-card'>
        <div class='dp-kpi-label'>Active</div>
        <div class='dp-kpi-value' style='color:#34D399;'>3</div>
        <div class='dp-kpi-trend-pos'>Under continuous recall</div>
    </div>
    """,
        unsafe_allow_html=True,
    )
with kp3:
    st.markdown(
        """
    <div class='dp-kpi-card'>
        <div class='dp-kpi-label'>On Hold</div>
        <div class='dp-kpi-value' style='color:#FBBF24;'>1</div>
        <div class='dp-kpi-trend-neg'>Constraint evaluation pending</div>
    </div>
    """,
        unsafe_allow_html=True,
    )
with kp4:
    st.markdown(
        """
    <div class='dp-kpi-card'>
        <div class='dp-kpi-label'>Completed</div>
        <div class='dp-kpi-value' style='color:#38BDF8;'>1</div>
        <div class='dp-kpi-trend-pos'>Archived with gold history</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

# 3. Project Overview Table (Screen 3 Reference Table)
st.markdown("<div class='dp-card'>", unsafe_allow_html=True)
st.markdown("### Active Project Directory")

st.markdown(
    """
    <table class='dp-table'>
        <thead>
            <tr>
                <th>Project</th>
                <th>Status</th>
                <th>Constraints</th>
                <th>Drift Risk</th>
                <th>Last Evaluated</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>
                    <div style='font-weight:700; color:#F8FAFC;'>Project Nova</div>
                    <div style='font-size:0.75rem; color:#94A3B8;'>Event Streaming Platform</div>
                </td>
                <td><span class='dp-badge' style='background:rgba(34,197,94,0.15); color:#4ADE80; border:1px solid rgba(74,222,128,0.35);'>ACTIVE</span></td>
                <td><code style='color:#818CF8;'>15</code></td>
                <td><span class='dp-badge' style='background:rgba(239,68,68,0.18); color:#F87171; border:1px solid rgba(248,113,113,0.5);'>HIGH</span></td>
                <td style='color:#94A3B8; font-size:0.82rem;'>2h ago</td>
            </tr>
            <tr>
                <td>
                    <div style='font-weight:700; color:#F8FAFC;'>Project Orion (Delta)</div>
                    <div style='font-size:0.75rem; color:#94A3B8;'>Data Platform Migration</div>
                </td>
                <td><span class='dp-badge' style='background:rgba(34,197,94,0.15); color:#4ADE80; border:1px solid rgba(74,222,128,0.35);'>ACTIVE</span></td>
                <td><code style='color:#818CF8;'>12</code></td>
                <td><span class='dp-badge' style='background:rgba(249,115,22,0.15); color:#FB923C; border:1px solid rgba(251,146,60,0.4);'>MEDIUM</span></td>
                <td style='color:#94A3B8; font-size:0.82rem;'>5h ago</td>
            </tr>
            <tr>
                <td>
                    <div style='font-weight:700; color:#F8FAFC;'>Project Helios (Beta)</div>
                    <div style='font-size:0.75rem; color:#94A3B8;'>ML Platform Gateway</div>
                </td>
                <td><span class='dp-badge' style='background:rgba(245,158,11,0.15); color:#FBBF24; border:1px solid rgba(251,191,36,0.35);'>ON HOLD</span></td>
                <td><code style='color:#818CF8;'>8</code></td>
                <td><span class='dp-badge' style='background:rgba(34,197,94,0.15); color:#4ADE80; border:1px solid rgba(74,222,128,0.35);'>LOW</span></td>
                <td style='color:#94A3B8; font-size:0.82rem;'>1d ago</td>
            </tr>
            <tr>
                <td>
                    <div style='font-weight:700; color:#F8FAFC;'>Project Zenith (Gamma)</div>
                    <div style='font-size:0.75rem; color:#94A3B8;'>Analytics Platform</div>
                </td>
                <td><span class='dp-badge' style='background:rgba(34,197,94,0.15); color:#4ADE80; border:1px solid rgba(74,222,128,0.35);'>ACTIVE</span></td>
                <td><code style='color:#818CF8;'>14</code></td>
                <td><span class='dp-badge' style='background:rgba(249,115,22,0.15); color:#FB923C; border:1px solid rgba(251,146,60,0.4);'>MEDIUM</span></td>
                <td style='color:#94A3B8; font-size:0.82rem;'>1d ago</td>
            </tr>
            <tr>
                <td>
                    <div style='font-weight:700; color:#F8FAFC;'>Project Atlas (Alpha)</div>
                    <div style='font-size:0.75rem; color:#94A3B8;'>Infrastructure Upgrade Baseline</div>
                </td>
                <td><span class='dp-badge' style='background:rgba(20,184,166,0.15); color:#5EEAD4; border:1px solid rgba(94,234,212,0.35);'>COMPLETED</span></td>
                <td><code style='color:#818CF8;'>6</code></td>
                <td><span class='dp-badge' style='background:rgba(34,197,94,0.15); color:#4ADE80; border:1px solid rgba(74,222,128,0.35);'>LOW</span></td>
                <td style='color:#94A3B8; font-size:0.82rem;'>3d ago</td>
            </tr>
        </tbody>
    </table>
    """,
    unsafe_allow_html=True,
)
st.markdown("</div>", unsafe_allow_html=True)

# 4. Project Drilldown & Real Backend Integration
st.markdown("### Inspect Project Context Constraints")

try:
    all_projects = backend.list_projects(role)
    proj_map = {p.project_id: p for p in all_projects}
    proj_options = list(proj_map.keys())
except Exception as e:  # noqa: BLE001
    st.error(f"Failed to fetch projects: {e}")
    proj_options = ["nova"]
    proj_map = {}

col_sel, col_space = st.columns([2, 3])
with col_sel:
    selected_pid = st.selectbox(
        "Select Project to Audit",
        proj_options,
        index=proj_options.index("nova") if "nova" in proj_options else 0,
    )

try:
    context = backend.get_project_context(selected_pid, role)
except ScopeError as se:
    st.warning(f"🔒 {se}")
    st.stop()
except Exception as e:  # noqa: BLE001
    st.error(f"Could not load context for {selected_pid}: {e}")
    st.stop()

# Active Drift Cards
st.markdown(f"#### Active Architectural Drift Cards for `{context.project_name}`")
try:
    drift_cards = backend.list_drift_cards(selected_pid, role)
    if drift_cards:
        for card in drift_cards:
            render_drift_card(card)
    else:
        st.info("No active decision drift recorded for this project.")
except Exception as e:  # noqa: BLE001
    st.error(f"Could not load drift cards: {e}")

# Context Constraints Table & Live Edit Form
c_const, c_edit = st.columns([3, 2])
with c_const:
    st.markdown("<div class='dp-card'>", unsafe_allow_html=True)
    st.markdown(f"**Operational Constraints for {context.project_name}:**")
    for k, v in context.constraints.items():
        st.markdown(f"- <code>{k}</code> = **{v}**", unsafe_allow_html=True)
    if context.updated_at:
        st.caption(f"Last updated: {context.updated_at.strftime('%Y-%m-%d %H:%M')}")
    st.markdown("</div>", unsafe_allow_html=True)

with c_edit, st.expander("✏️ Update / Add Constraint", expanded=False):
    key_name = st.text_input("Constraint Key", placeholder="e.g. consumer_count, ops_capacity")
    key_val = st.text_input("New Value", placeholder="e.g. 25, medium, high")

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
