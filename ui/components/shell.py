"""Application chrome and shell components — top bar, sidebar profile, and breadcrumbs."""

from __future__ import annotations

import os

import streamlit as st

from ui.components.icons import get_icon_svg


def render_top_bar(
    active_stage: str = "DECIDE", search_placeholder: str = "Search decisions, projects, or keywords..."
) -> None:
    """Render the enterprise top bar with workflow breadcrumbs, search, and user actions."""
    stages = ["CAPTURE", "ANALYZE", "LEARN", "DECIDE"]
    breadcrumb_parts = []
    for s in stages:
        if s == active_stage.upper():
            breadcrumb_parts.append(f"<span class='dp-breadcrumb-active'>{s}</span>")
        else:
            breadcrumb_parts.append(f"<span class='dp-breadcrumb-idle'>{s}</span>")
    breadcrumbs_html = " <span class='dp-breadcrumb-sep'>/</span> ".join(breadcrumb_parts)

    search_icon = get_icon_svg("search", size=16, color="#94A3B8")
    bell_icon = get_icon_svg("bell", size=17, color="#CBD5E1")
    moon_icon = get_icon_svg("moon", size=17, color="#CBD5E1")
    logo_icon = get_icon_svg("logo_bubble", size=22, color="#818CF8")

    st.markdown(
        f"""
    <div class='dp-topbar'>
        <div class='dp-topbar-left'>
            <div class='dp-topbar-brand'>
                {logo_icon}
                <span class='dp-topbar-title'>DecisionPrint</span>
                <span class='dp-topbar-tagline'>Organizational Memory for Better Decisions</span>
            </div>
        </div>
        <div class='dp-topbar-center'>
            <div class='dp-topbar-search'>
                {search_icon}
                <span class='dp-search-placeholder'>{search_placeholder}</span>
            </div>
        </div>
        <div class='dp-topbar-right'>
            <div class='dp-breadcrumbs'>
                {breadcrumbs_html}
            </div>
            <div class='dp-topbar-actions'>
                <div class='dp-icon-btn' title='Notifications'>{bell_icon}</div>
                <div class='dp-icon-btn' title='Theme: Dark'>{moon_icon}</div>
                <div class='dp-user-avatar' title='John Doe (Product Manager)'>JD</div>
            </div>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )


def render_sidebar_chrome() -> None:
    """Render the unified sidebar shell with brand, role switcher, and user profile."""
    logo_icon = get_icon_svg("logo_bubble", size=26, color="#818CF8")

    st.sidebar.markdown(
        f"""
    <div class='dp-sidebar-header'>
        <div class='dp-sidebar-logo-group'>
            {logo_icon}
            <div>
                <div class='dp-sidebar-brand-name'>DecisionPrint</div>
                <div class='dp-sidebar-brand-sub'>Architecture Intelligence</div>
            </div>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Role selector
    current_role = st.session_state.get("role") or "admin"
    roles = ["engineer", "project_lead", "executive", "admin"]
    default_role_idx = roles.index(current_role) if current_role in roles else 3

    st.sidebar.markdown("<div class='dp-sidebar-divider'></div>", unsafe_allow_html=True)
    selected_role = st.sidebar.selectbox(
        "Active Role",
        roles,
        index=default_role_idx,
        key="app_role_selector",
        help="Switch role to test Role-Based Access Control (RBAC) and permissions.",
    )
    if selected_role != st.session_state.get("role"):
        st.session_state.role = selected_role

    backend = os.getenv("DP_BACKEND", "fixture")
    backend_status = "Connected"
    shield_icon = get_icon_svg("shield", size=13, color="#34D399")

    st.sidebar.markdown(
        f"""
    <div class='dp-sidebar-status-card'>
        <div class='dp-sidebar-status-pill'>
            <span class='dp-status-dot'></span>
            <span>BACKEND: <strong>{backend.upper()}</strong></span>
        </div>
        <div class='dp-sidebar-status-detail'>{shield_icon} <span>Database & Memory {backend_status}</span></div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.sidebar.markdown("<div class='dp-sidebar-spacer'></div>", unsafe_allow_html=True)

    # User Profile at bottom
    st.sidebar.markdown(
        """
    <div class='dp-sidebar-user-card'>
        <div class='dp-user-avatar-lg'>JD</div>
        <div class='dp-user-info'>
            <div class='dp-user-name'>John Doe</div>
            <div class='dp-user-role'>Product Manager</div>
        </div>
    </div>
    <div class='dp-sidebar-version'>v3.2.0-enterprise · Austin, TX</div>
    """,
        unsafe_allow_html=True,
    )
