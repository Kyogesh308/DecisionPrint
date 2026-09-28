"""Application chrome and shell components — top bar, sidebar profile, and breadcrumbs."""

from __future__ import annotations

import os

import streamlit as st

from ui.components.icons import get_icon_svg


def set_theme(theme_name: str) -> None:
    """Synchronize theme state across all widgets and preferences."""
    st.session_state["theme"] = theme_name
    st.session_state["app_theme_radio_sidebar"] = theme_name
    if "settings_theme_radio" in st.session_state:
        st.session_state["settings_theme_radio"] = theme_name


def render_top_bar(
    active_stage: str = "DECIDE", search_placeholder: str = "Search decisions, projects, or keywords..."
) -> None:
    """Render the enterprise top bar with workflow breadcrumbs, interactive search, and working theme toggle."""
    stages = ["CAPTURE", "ANALYZE", "LEARN", "DECIDE"]
    breadcrumb_parts = []
    for s in stages:
        if s == active_stage.upper():
            breadcrumb_parts.append(f"<span class='dp-breadcrumb-active'>{s}</span>")
        else:
            breadcrumb_parts.append(f"<span class='dp-breadcrumb-idle'>{s}</span>")
    breadcrumbs_html = " <span class='dp-breadcrumb-sep'>/</span> ".join(breadcrumb_parts)

    current_theme = st.session_state.get("theme", "light")
    is_dark = current_theme == "dark"
    next_theme = "light" if is_dark else "dark"
    theme_btn_label = "☀️ Light" if is_dark else "🌙 Dark"
    logo_icon = get_icon_svg("logo_bubble", size=22, color="var(--dp-primary, #2563EB)")

    # Render top bar in an elevated native bordered card
    with st.container(border=True):
        col_brand, col_search, col_bread, col_actions = st.columns([3.2, 3.4, 2.2, 1.2], vertical_alignment="center")

        with col_brand:
            st.markdown(
                f"""
                <div class='dp-topbar-brand'>
                    {logo_icon}
                    <div style='display:inline-block; margin-left:6px;'>
                        <span class='dp-topbar-title'>DecisionPrint</span>
                        <span class='dp-topbar-tagline'>Memory for Decisions</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col_search:
            search_query = st.text_input(
                "Global Search",
                value=st.session_state.get("global_search", ""),
                placeholder=search_placeholder,
                key=f"topbar_search_input_{active_stage}",
                label_visibility="collapsed",
            )
            if search_query != st.session_state.get("global_search", ""):
                st.session_state.global_search = search_query

        with col_bread:
            st.markdown(
                f"""
                <div class='dp-breadcrumbs-wrapper'>
                    {breadcrumbs_html}
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col_actions:
            act_col1, act_col2 = st.columns([1.3, 0.7], vertical_alignment="center")
            with act_col1:
                if st.button(
                    theme_btn_label,
                    key=f"topbar_theme_btn_{active_stage}",
                    help=f"Switch to {next_theme.capitalize()} Theme",
                    use_container_width=True,
                ):
                    set_theme(next_theme)
                    st.rerun()
            with act_col2:
                st.markdown(
                    """
                    <div style='display:flex; justify-content:center; align-items:center; height:100%;'>
                        <div class='dp-user-avatar' title='John Doe (Product Manager)'>JD</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


def render_sidebar_chrome() -> None:
    """Render the unified sidebar shell with brand, role switcher, and theme selector."""
    logo_icon = get_icon_svg("logo_bubble", size=26, color="var(--dp-primary, #2563EB)")

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
        st.rerun()

    # Theme Mode Selector (Segmented Radio)
    current_theme = st.session_state.get("theme", "light")
    if (
        "app_theme_radio_sidebar" not in st.session_state
        or st.session_state.get("app_theme_radio_sidebar") != current_theme
    ):
        st.session_state["app_theme_radio_sidebar"] = current_theme

    theme_options = ["light", "dark", "system"]
    theme_labels = {"light": "☀️ Light", "dark": "🌙 Dark", "system": "💻 System"}
    selected_theme = st.sidebar.radio(
        "Workspace Theme",
        theme_options,
        format_func=lambda x: theme_labels.get(x, x),
        horizontal=True,
        key="app_theme_radio_sidebar",
        help="Switch between Full Light, Full Dark, or System mode.",
    )
    if selected_theme != st.session_state.get("theme"):
        set_theme(selected_theme)
        st.rerun()

    backend = os.getenv("DP_BACKEND", "fixture")
    backend_status = "Connected"
    shield_icon = get_icon_svg("shield", size=13, color="var(--dp-success, #16A34A)")

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
