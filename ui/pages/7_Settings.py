"""Settings page — Global app configuration, role management, and backend integrations matching Screen 8."""

from __future__ import annotations

import os

import streamlit as st

from ui.adapters import get_backend
from ui.components import (
    inject_custom_css,
    render_html,
    render_sidebar_chrome,
    render_top_bar,
)
from ui.components._state import init_session_state
from ui.components.dialogs import check_and_render_evidence_dialog
from ui.components.shell import set_theme

init_session_state()

if not st.session_state.get("_top_nav_active"):
    inject_custom_css()
    render_top_bar(active_stage="DECIDE", search_placeholder="Search settings...")
    render_sidebar_chrome()

backend = get_backend()
role = st.session_state.get("role") or "admin"
check_and_render_evidence_dialog(backend, role)

# 1. Header
render_html(
    """
    <div style='margin-bottom: 1.25rem;'>
        <h1 style='margin-bottom: 0.25rem;'>Settings</h1>
        <p style='color:var(--dp-text-secondary); font-size:1.02rem; margin:0;'>
            Configure your enterprise workspace, role permissions, and backend integration preferences.
        </p>
    </div>
    """
)

# 2. Four Settings Tabs matching Screen 8
tab_general, tab_role, tab_backend, tab_appearance = st.tabs(
    ["General", "Role & Access", "Backend Configuration", "Appearance & Design"]
)

with tab_general:
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

with tab_role:
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
    render_html(
        f"<div style='color:var(--dp-primary); font-size:0.9rem; margin-top:0.4rem; font-weight:500;'>{role_descriptions.get(role, '')}</div>"
    )

    render_html("<div style='height: 1rem;'></div>")
    st.markdown("#### RBAC Permission Scope Matrix")
    render_html(
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
                    <td><span style='color:var(--dp-success); font-weight:600;'>Yes</span></td>
                    <td><span style='color:var(--dp-success); font-weight:600;'>Yes</span></td>
                    <td><span style='color:var(--dp-success); font-weight:600;'>Yes</span></td>
                    <td><span style='color:var(--dp-success); font-weight:600;'>Yes</span></td>
                </tr>
                <tr>
                    <td>View Public Decisions</td>
                    <td><span style='color:var(--dp-success); font-weight:600;'>Yes</span></td>
                    <td><span style='color:var(--dp-success); font-weight:600;'>Yes</span></td>
                    <td><span style='color:var(--dp-success); font-weight:600;'>Yes</span></td>
                    <td><span style='color:var(--dp-success); font-weight:600;'>Yes</span></td>
                </tr>
                <tr>
                    <td>Confidential Records (Project Delta)</td>
                    <td><span style='color:var(--dp-danger); font-weight:600;'>Blocked (ScopeError)</span></td>
                    <td><span style='color:var(--dp-danger); font-weight:600;'>Blocked</span></td>
                    <td><span style='color:var(--dp-success); font-weight:600;'>Yes</span></td>
                    <td><span style='color:var(--dp-success); font-weight:600;'>Yes</span></td>
                </tr>
                <tr>
                    <td>Ingest Document Sources</td>
                    <td><span style='color:var(--dp-text-muted);'>Review queue</span></td>
                    <td><span style='color:var(--dp-success); font-weight:600;'>Yes</span></td>
                    <td><span style='color:var(--dp-success); font-weight:600;'>Yes</span></td>
                    <td><span style='color:var(--dp-success); font-weight:600;'>Yes</span></td>
                </tr>
            </tbody>
        </table>
        """
    )

with tab_backend:
    st.markdown("### Backend & Infrastructure Services")
    st.caption("Configured services. Configuration status does not imply a remote health check.")

    current_backend = os.getenv("DP_BACKEND", "fixture").lower()
    db_path = os.getenv("DP_DB_PATH", "var/decisionprint.db")
    hindsight_configured = bool(os.getenv("DP_HINDSIGHT_BASE_URL"))
    llm_configured = bool(os.getenv("DP_LLM_API_KEY"))

    c_b1, c_b2 = st.columns(2)
    with c_b1:
        st.markdown(f"**Application database:** SQLite (`{db_path}`)")
        st.markdown(f"**LLM extraction:** {'Configured' if llm_configured else 'Not configured'}")

    with c_b2:
        st.markdown(f"**UI adapter:** {'Fixture demo' if current_backend == 'fixture' else current_backend.upper()}")
        st.markdown(f"**Hindsight memory:** {'Configured' if hindsight_configured else 'Using local default endpoint'}")

with tab_appearance:
    st.markdown("### Interface Theme & Mode")
    st.caption("Select your preferred visual appearance across all DecisionPrint dashboards:")

    current_theme = st.session_state.get("theme", "light")
    if "settings_theme_radio" not in st.session_state or st.session_state.get("settings_theme_radio") != current_theme:
        st.session_state["settings_theme_radio"] = current_theme

    theme_options = ["light", "dark", "system"]
    theme_choice = st.radio(
        "Theme Mode",
        theme_options,
        format_func=lambda x: {
            "light": "☀️ Light Theme (Enterprise SaaS Default)",
            "dark": "🌙 Dark Theme (Midnight Slate)",
            "system": "💻 System Preference",
        }[x],
        horizontal=True,
        key="settings_theme_radio",
    )
    if theme_choice != st.session_state.get("theme"):
        set_theme(theme_choice)
        st.rerun()

    render_html("<div style='height: 1rem;'></div>")
    st.markdown("#### Enterprise Design Tokens")
    st.caption("Active tokens configured for the enterprise design system:")

    render_html(
        """
        <div style='display:flex; gap:1rem; flex-wrap:wrap; margin: 1rem 0;'>
            <div style='display:flex; align-items:center; gap:0.5rem;'>
                <div style='width:24px; height:24px; border-radius:6px; background:var(--dp-surface-page); border:1px solid var(--dp-border);'></div>
                <span style='font-size:0.8rem; font-family:"JetBrains Mono", monospace;'>Canvas (var(--dp-surface-page))</span>
            </div>
            <div style='display:flex; align-items:center; gap:0.5rem;'>
                <div style='width:24px; height:24px; border-radius:6px; background:var(--dp-surface-card); border:1px solid var(--dp-border);'></div>
                <span style='font-size:0.8rem; font-family:"JetBrains Mono", monospace;'>Surface (var(--dp-surface-card))</span>
            </div>
            <div style='display:flex; align-items:center; gap:0.5rem;'>
                <div style='width:24px; height:24px; border-radius:6px; background:var(--dp-primary); border:1px solid var(--dp-primary);'></div>
                <span style='font-size:0.8rem; font-family:"JetBrains Mono", monospace;'>Primary Accent (var(--dp-primary))</span>
            </div>
            <div style='display:flex; align-items:center; gap:0.5rem;'>
                <div style='width:24px; height:24px; border-radius:6px; background:var(--dp-success);'></div>
                <span style='font-size:0.8rem; font-family:"JetBrains Mono", monospace;'>Success (var(--dp-success))</span>
            </div>
            <div style='display:flex; align-items:center; gap:0.5rem;'>
                <div style='width:24px; height:24px; border-radius:6px; background:var(--dp-danger);'></div>
                <span style='font-size:0.8rem; font-family:"JetBrains Mono", monospace;'>Critical (var(--dp-danger))</span>
            </div>
        </div>
        """
    )
