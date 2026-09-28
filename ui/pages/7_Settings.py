"""Settings page — Global app configuration, role management, and backend integrations matching Screen 8."""

from __future__ import annotations

import os

import streamlit as st

from ui.adapters import get_backend
from ui.components import (
    inject_custom_css,
    render_sidebar_chrome,
    render_top_bar,
)
from ui.components.dialogs import check_and_render_evidence_dialog

inject_custom_css()

backend = get_backend()
role = st.session_state.get("role") or "admin"

render_top_bar(active_stage="DECIDE", search_placeholder="Search settings...")
render_sidebar_chrome()
check_and_render_evidence_dialog(backend, role)

# 1. Header
st.markdown(
    """
    <div style='margin-bottom: 1.25rem;'>
        <h1 style='margin-bottom: 0.25rem;'>Settings</h1>
        <p style='color:#94A3B8; font-size:1.02rem; margin:0;'>
            Configure your enterprise workspace, role permissions, and backend integration preferences.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# 2. Four Settings Tabs matching Screen 8
tab_general, tab_role, tab_backend, tab_appearance = st.tabs(
    ["General", "Role & Access", "Backend Configuration", "Appearance & Design"]
)

with tab_general:
    st.markdown("<div class='dp-card'>", unsafe_allow_html=True)
    st.markdown("### General Workspace Settings")
    st.caption("Manage enterprise workspace identifiers and localization defaults:")

    c_org, c_def = st.columns(2)
    with c_org:
        st.text_input("Organization Name", value="Northstar Systems / Acme Corp")
        st.selectbox("Language", ["English (United States)", "English (UK)", "German", "Japanese"], index=0)
    with c_def:
        st.selectbox(
            "Default Active Project", ["Project Nova", "Project Orion", "Project Helios", "Project Zenith"], index=0
        )
        st.selectbox(
            "Timezone", ["UTC", "America/Chicago (CST)", "America/New_York (EST)", "Europe/London (GMT)"], index=1
        )

    if st.button("Save General Preferences", type="primary"):
        st.success("General preferences updated successfully.")
    st.markdown("</div>", unsafe_allow_html=True)

with tab_role:
    st.markdown("<div class='dp-card'>", unsafe_allow_html=True)
    st.markdown("### Role & Access Control (RBAC)")
    st.caption("Manage active session authorization and inspect permission boundaries:")

    roles = ["engineer", "project_lead", "executive", "admin"]
    current_role_idx = roles.index(role) if role in roles else 3

    new_role = st.selectbox(
        "Your Role",
        roles,
        index=current_role_idx,
        help="Select role to evaluate access restrictions in real time.",
    )
    if new_role != st.session_state.get("role"):
        st.session_state.role = new_role
        st.rerun()

    role_descriptions = {
        "admin": "Full access to all features, confidential records, document ingestion, and configuration.",
        "executive": "Read-only access to all projects including confidential cost-cutting and postmortem records.",
        "project_lead": "Access to active project constraints, briefs, and team architectural evolution.",
        "engineer": "Access to standard engineering decisions. Confidential records (e.g. Project Delta) require elevated permissions.",
    }
    st.markdown(
        f"<div style='color:#38BDF8; font-size:0.9rem; margin-top:0.4rem;'>{role_descriptions.get(role, '')}</div>",
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
    st.markdown("#### RBAC Permission Scope Matrix")
    st.markdown(
        """
        <table class='dp-table'>
            <thead>
                <tr>
                    <th>Capability</th>
                    <th>Engineer</th>
                    <th>Project Lead</th>
                    <th>Executive</th>
                    <th>Admin</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Recall Memory (Ask)</td>
                    <td><span style='color:#34D399;'>Yes</span></td>
                    <td><span style='color:#34D399;'>Yes</span></td>
                    <td><span style='color:#34D399;'>Yes</span></td>
                    <td><span style='color:#34D399;'>Yes</span></td>
                </tr>
                <tr>
                    <td>View Public Decisions</td>
                    <td><span style='color:#34D399;'>Yes</span></td>
                    <td><span style='color:#34D399;'>Yes</span></td>
                    <td><span style='color:#34D399;'>Yes</span></td>
                    <td><span style='color:#34D399;'>Yes</span></td>
                </tr>
                <tr>
                    <td>Confidential Records (Project Delta)</td>
                    <td><span style='color:#F87171;'>Blocked (ScopeError)</span></td>
                    <td><span style='color:#F87171;'>Blocked</span></td>
                    <td><span style='color:#34D399;'>Yes</span></td>
                    <td><span style='color:#34D399;'>Yes</span></td>
                </tr>
                <tr>
                    <td>Ingest Document Sources</td>
                    <td><span style='color:#94A3B8;'>Review queue</span></td>
                    <td><span style='color:#34D399;'>Yes</span></td>
                    <td><span style='color:#34D399;'>Yes</span></td>
                    <td><span style='color:#34D399;'>Yes</span></td>
                </tr>
            </tbody>
        </table>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

with tab_backend:
    st.markdown("<div class='dp-card'>", unsafe_allow_html=True)
    st.markdown("### Backend & Infrastructure Services")
    st.caption("Active connection health and protocol adapters:")

    current_backend = os.getenv("DP_BACKEND", "fixture")

    c_b1, c_b2 = st.columns(2)
    with c_b1:
        st.markdown(
            """
            <div style='padding:0.75rem 0;'>
                <div style='font-size:0.85rem; color:#94A3B8;'>Database</div>
                <div style='display:flex; align-items:center; gap:0.6rem; margin-top:0.25rem;'>
                    <strong style='font-size:1.05rem;'>PostgreSQL 16</strong>
                    <span class='dp-badge' style='background:rgba(34,197,94,0.15); color:#4ADE80; border:1px solid rgba(74,222,128,0.4);'>CONNECTED</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            """
            <div style='padding:0.75rem 0;'>
                <div style='font-size:0.85rem; color:#94A3B8;'>LLM Reasoning & Synthesis</div>
                <div style='display:flex; align-items:center; gap:0.6rem; margin-top:0.25rem;'>
                    <strong style='font-size:1.05rem;'>Gemini 1.5 Pro / Claude 3.5</strong>
                    <span class='dp-badge' style='background:rgba(34,197,94,0.15); color:#4ADE80; border:1px solid rgba(74,222,128,0.4);'>CONNECTED</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c_b2:
        st.markdown(
            f"""
            <div style='padding:0.75rem 0;'>
                <div style='font-size:0.85rem; color:#94A3B8;'>Active Adapter Protocol</div>
                <div style='display:flex; align-items:center; gap:0.6rem; margin-top:0.25rem;'>
                    <strong style='font-size:1.05rem;'>{current_backend.upper()} BACKEND</strong>
                    <span class='dp-badge' style='background:rgba(99,102,241,0.15); color:#818CF8; border:1px solid #6366F1;'>OPERATIONAL</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            """
            <div style='padding:0.75rem 0;'>
                <div style='font-size:0.85rem; color:#94A3B8;'>Vector Memory Index</div>
                <div style='display:flex; align-items:center; gap:0.6rem; margin-top:0.25rem;'>
                    <strong style='font-size:1.05rem;'>Hindsight Multi-Tenant Vector Store</strong>
                    <span class='dp-badge' style='background:rgba(34,197,94,0.15); color:#4ADE80; border:1px solid rgba(74,222,128,0.4);'>SYNCHRONIZED</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)

with tab_appearance:
    st.markdown("<div class='dp-card'>", unsafe_allow_html=True)
    st.markdown("### Enterprise Theme & Tokens")
    st.caption("Modern Dark (Cinema Mobile / Pro Dev SaaS) design system tokens:")

    st.markdown(
        """
        <div style='display:flex; gap:1rem; flex-wrap:wrap; margin: 1rem 0;'>
            <div style='display:flex; align-items:center; gap:0.5rem;'>
                <div style='width:24px; height:24px; border-radius:6px; background:#080D1A; border:1px solid #334155;'></div>
                <span style='font-size:0.8rem; font-family:"JetBrains Mono", monospace;'>Canvas #080D1A</span>
            </div>
            <div style='display:flex; align-items:center; gap:0.5rem;'>
                <div style='width:24px; height:24px; border-radius:6px; background:#111827; border:1px solid #334155;'></div>
                <span style='font-size:0.8rem; font-family:"JetBrains Mono", monospace;'>Slate Panel #111827</span>
            </div>
            <div style='display:flex; align-items:center; gap:0.5rem;'>
                <div style='width:24px; height:24px; border-radius:6px; background:#6366F1;'></div>
                <span style='font-size:0.8rem; font-family:"JetBrains Mono", monospace;'>Indigo Accent #6366F1</span>
            </div>
            <div style='display:flex; align-items:center; gap:0.5rem;'>
                <div style='width:24px; height:24px; border-radius:6px; background:#38BDF8;'></div>
                <span style='font-size:0.8rem; font-family:"JetBrains Mono", monospace;'>Cyan Highlight #38BDF8</span>
            </div>
            <div style='display:flex; align-items:center; gap:0.5rem;'>
                <div style='width:24px; height:24px; border-radius:6px; background:#10B981;'></div>
                <span style='font-size:0.8rem; font-family:"JetBrains Mono", monospace;'>Emerald Success #10B981</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)
