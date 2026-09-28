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
    if st.session_state.get("_top_nav_active", False):
        return

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
    if st.session_state.get("_top_nav_active", False):
        return
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


def get_nav_badges(backend: object = None, role: str = "admin", project_id: str = "nova") -> dict[str, object]:
    """Calculate dynamic badge counters for navigation items safely."""
    badges: dict[str, object] = {
        "explorer_queue": 0,
        "high_drift_count": 0,
        "ingest_updated": False,
    }
    if not backend:
        return badges
    try:
        queue = getattr(backend, "list_review_queue", list)()
        badges["explorer_queue"] = len(queue)
    except Exception:  # noqa: BLE001
        badges["explorer_queue"] = 0

    try:
        drift_cards = getattr(backend, "list_drift_cards", lambda _p: [])(project_id)
        badges["high_drift_count"] = sum(
            1 for d in drift_cards if getattr(d, "level", None) and d.level.value.lower() == "high"
        )
    except Exception:  # noqa: BLE001
        badges["high_drift_count"] = 0

    badges["ingest_updated"] = bool(st.session_state.get("ingest_flag", False))
    return badges


def render_nav_context_bar(backend: object = None) -> None:
    """Render the persistent under-nav context bar matching v3 spec."""
    if backend is None:
        try:
            from ui.adapters import get_backend

            backend = get_backend()
        except Exception:  # noqa: BLE001
            backend = None

    # Retrieve projects safely
    projects = []
    if backend:
        try:
            projects = getattr(backend, "list_projects", list)()
        except Exception:  # noqa: BLE001
            projects = []
    if not projects:
        project_ids = ["nova", "alpha", "beta", "gamma", "delta"]
    else:
        project_ids = [getattr(p, "project_id", str(p)) for p in projects]

    cur_project = st.session_state.get("project_id") or "nova"
    if cur_project not in project_ids and project_ids:
        cur_project = project_ids[0]
    p_idx = project_ids.index(cur_project) if cur_project in project_ids else 0

    roles = ["engineer", "project_lead", "executive", "admin"]
    cur_role = st.session_state.get("role") or "admin"
    r_idx = roles.index(cur_role) if cur_role in roles else 3

    current_backend = os.getenv("DP_BACKEND", "fixture").upper()

    # Calculate last updated relative time
    last_updated_str = "just now"
    if backend:
        try:
            overview = getattr(backend, "get_memory_overview", lambda r: None)(cur_role)
            if overview and getattr(overview, "last_updated", None):
                dt = overview.last_updated
                last_updated_str = dt.strftime("%b %d, %H:%M")
        except Exception:  # noqa: BLE001, S110
            pass

    # Return chip if returning from deep link
    return_to = st.session_state.get("return_to")

    with st.container():
        cols = st.columns([2.0, 1.8, 1.4, 2.0, 1.6], vertical_alignment="center")

        with cols[0]:
            sel_proj = st.selectbox(
                "Project",
                project_ids,
                index=p_idx,
                format_func=lambda x: f"📁 Project {x.capitalize()}",
                key="_ctx_project_selector",
                label_visibility="collapsed",
            )
            if sel_proj != st.session_state.get("project_id"):
                st.session_state["project_id"] = sel_proj
                st.rerun()

        with cols[1]:
            sel_role = st.selectbox(
                "Role",
                roles,
                index=r_idx,
                format_func=lambda x: f"👤 {x.replace('_', ' ').capitalize()}",
                key="_ctx_role_selector",
                label_visibility="collapsed",
            )
            if sel_role != st.session_state.get("role"):
                st.session_state["role"] = sel_role
                st.rerun()

        with cols[2]:
            st.markdown(
                f"""
                <span class='dp-badge' style='background:var(--card, #FFFFFF); color:var(--ink, #111111);
                      border:1.5px solid var(--ink, #111111); border-bottom:3px solid var(--ink, #111111);
                      border-radius:999px; padding:4px 10px; font-weight:700; font-size:0.75rem; letter-spacing:0.04em;'>
                    ⚡ {current_backend}
                </span>
                """,
                unsafe_allow_html=True,
            )

        with cols[3]:
            st.markdown(
                f"""
                <span style='font-size:0.78rem; font-weight:600; color:var(--muted, #8A8A8A);
                      font-family:"JetBrains Mono", monospace;'>
                    🕒 Memory updated: {last_updated_str}
                </span>
                """,
                unsafe_allow_html=True,
            )

        with cols[4]:
            if return_to:
                if st.button(f"← Back to {return_to}", key="_btn_return_deep_link", type="secondary"):
                    st.session_state["return_to"] = None
                    target_page = f"pages/{return_to}.py" if not return_to.endswith(".py") else return_to
                    try:
                        st.switch_page(target_page)
                    except Exception:  # noqa: BLE001
                        st.rerun()
            else:
                theme = st.session_state.get("theme", "light")
                is_dark = theme == "dark"
                next_t = "light" if is_dark else "dark"
                t_icon = "☀️ Light" if is_dark else "🌙 Dark"
                if st.button(
                    t_icon,
                    key="_btn_theme_toggle_ctx",
                    help=f"Switch to {next_t.capitalize()} Mode",
                ):
                    set_theme(next_t)
                    st.rerun()

    st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
