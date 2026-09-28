"""Design tokens and theme injection — light-first enterprise SaaS UI with full dark mode support."""

from __future__ import annotations

import streamlit as st

__all__ = [
    "CAUSAL_COLORS",
    "COMPARISON_COLORS",
    "DRIFT_COLORS",
    "EPISTEMIC_COLORS",
    "STATUS_COLORS",
    "badge_html",
    "get_current_theme",
    "inject_custom_css",
    "set_current_theme",
]

# Epistemic types (Fact, Observation, Inference, Recommendation)
EPISTEMIC_COLORS = {
    "fact": {
        "light_bg": "#EAF2FF",
        "light_text": "#245AC7",
        "light_border": "#C3D7FA",
        "dark_bg": "rgba(59, 130, 246, 0.15)",
        "dark_text": "#60A5FA",
        "dark_border": "rgba(96, 165, 250, 0.35)",
        "label": "FACT",
    },
    "observation": {
        "light_bg": "#E6F7F5",
        "light_text": "#087F8C",
        "light_border": "#B0EBE4",
        "dark_bg": "rgba(20, 184, 166, 0.15)",
        "dark_text": "#5EEAD4",
        "dark_border": "rgba(94, 234, 212, 0.35)",
        "label": "OBSERVATION",
    },
    "inference": {
        "light_bg": "#FFF4DE",
        "light_text": "#A85B08",
        "light_border": "#FDE3B2",
        "dark_bg": "rgba(245, 158, 11, 0.15)",
        "dark_text": "#FBBF24",
        "dark_border": "rgba(251, 191, 36, 0.35)",
        "label": "INFERENCE",
    },
    "recommendation": {
        "light_bg": "#F3EFFF",
        "light_text": "#7958D8",
        "light_border": "#DFD5FA",
        "dark_bg": "rgba(168, 85, 247, 0.15)",
        "dark_text": "#C084FC",
        "dark_border": "rgba(192, 132, 252, 0.35)",
        "label": "RECOMMENDATION",
    },
}

# Drift levels
DRIFT_COLORS = {
    "none": {
        "light_bg": "#E8F6EE",
        "light_text": "#18794E",
        "light_border": "#C2EBD4",
        "dark_bg": "rgba(34, 197, 94, 0.15)",
        "dark_text": "#4ADE80",
        "dark_border": "rgba(74, 222, 128, 0.4)",
        "bg": "#E8F6EE",
        "text": "#18794E",
        "border": "#C2EBD4",
        "label": "NO DRIFT",
    },
    "low": {
        "light_bg": "#E8F6EE",
        "light_text": "#18794E",
        "light_border": "#C2EBD4",
        "dark_bg": "rgba(34, 197, 94, 0.15)",
        "dark_text": "#4ADE80",
        "dark_border": "rgba(74, 222, 128, 0.4)",
        "bg": "#E8F6EE",
        "text": "#18794E",
        "border": "#C2EBD4",
        "label": "LOW DRIFT",
    },
    "medium": {
        "light_bg": "#FFF4DE",
        "light_text": "#A85B08",
        "light_border": "#FDE3B2",
        "dark_bg": "rgba(249, 115, 22, 0.15)",
        "dark_text": "#FB923C",
        "dark_border": "rgba(251, 146, 60, 0.4)",
        "bg": "#FFF4DE",
        "text": "#A85B08",
        "border": "#FDE3B2",
        "label": "MEDIUM DRIFT",
    },
    "high": {
        "light_bg": "#FDECEE",
        "light_text": "#B42332",
        "light_border": "#F9CCD1",
        "dark_bg": "rgba(239, 68, 68, 0.18)",
        "dark_text": "#F87171",
        "dark_border": "rgba(248, 113, 113, 0.5)",
        "bg": "#FDECEE",
        "text": "#B42332",
        "border": "#F9CCD1",
        "label": "HIGH DRIFT",
    },
}

# Comparison badges
COMPARISON_COLORS = {
    "same": {
        "light_bg": "#EEF2F8",
        "light_text": "#52627A",
        "light_border": "#DCE3ED",
        "dark_bg": "rgba(148, 163, 184, 0.12)",
        "dark_text": "#94A3B8",
        "dark_border": "rgba(148, 163, 184, 0.25)",
        "label": "UNCHANGED",
    },
    "changed": {
        "light_bg": "#FDECEE",
        "light_text": "#B42332",
        "light_border": "#F9CCD1",
        "dark_bg": "rgba(239, 68, 68, 0.15)",
        "dark_text": "#F87171",
        "dark_border": "rgba(248, 113, 113, 0.35)",
        "label": "CHANGED",
    },
    "newly_present": {
        "light_bg": "#FFF4DE",
        "light_text": "#A85B08",
        "light_border": "#FDE3B2",
        "dark_bg": "rgba(249, 115, 22, 0.15)",
        "dark_text": "#FB923C",
        "dark_border": "rgba(251, 146, 60, 0.35)",
        "label": "NEW",
    },
    "unknown": {
        "light_bg": "#EEF2F8",
        "light_text": "#68778D",
        "light_border": "#DCE3ED",
        "dark_bg": "rgba(100, 116, 139, 0.12)",
        "dark_text": "#64748B",
        "dark_border": "rgba(100, 116, 139, 0.2)",
        "label": "UNKNOWN",
    },
    "incomparable": {
        "light_bg": "#EEF2F8",
        "light_text": "#68778D",
        "light_border": "#DCE3ED",
        "dark_bg": "rgba(100, 116, 139, 0.12)",
        "dark_text": "#64748B",
        "dark_border": "rgba(100, 116, 139, 0.2)",
        "label": "N/A",
    },
}

# Causal link labels
CAUSAL_COLORS = {
    "explicit_causal_link": {
        "light_bg": "#EAF0FF",
        "light_text": "#315EDE",
        "light_border": "#315EDE",
        "dark_bg": "rgba(99, 102, 241, 0.22)",
        "dark_text": "#818CF8",
        "dark_border": "#6366F1",
        "label": "EXPLICIT CAUSAL LINK",
    },
    "strong_evidence": {
        "light_bg": "#E6F7F5",
        "light_text": "#087F8C",
        "light_border": "#B0EBE4",
        "dark_bg": "rgba(20, 184, 166, 0.18)",
        "dark_text": "#5EEAD4",
        "dark_border": "rgba(94, 234, 212, 0.4)",
        "label": "STRONG EVIDENCE",
    },
    "possible_causal_link": {
        "light_bg": "#FFF4DE",
        "light_text": "#A85B08",
        "light_border": "#FDE3B2",
        "dark_bg": "rgba(245, 158, 11, 0.18)",
        "dark_text": "#FBBF24",
        "dark_border": "rgba(251, 191, 36, 0.4)",
        "label": "POSSIBLE LINK",
    },
    "fact": {
        "light_bg": "#EAF2FF",
        "light_text": "#245AC7",
        "light_border": "#C3D7FA",
        "dark_bg": "rgba(59, 130, 246, 0.18)",
        "dark_text": "#60A5FA",
        "dark_border": "rgba(96, 165, 250, 0.4)",
        "label": "DOCUMENTED FACT",
    },
    "none": {
        "light_bg": "transparent",
        "light_text": "",
        "light_border": "transparent",
        "dark_bg": "transparent",
        "dark_text": "",
        "dark_border": "transparent",
        "label": "",
    },
}

# Decision & Lifecycle status
STATUS_COLORS = {
    "active": {
        "light_bg": "#E8F6EE",
        "light_text": "#18794E",
        "light_border": "#C2EBD4",
        "dark_bg": "rgba(34, 197, 94, 0.15)",
        "dark_text": "#4ADE80",
        "dark_border": "rgba(74, 222, 128, 0.35)",
        "label": "ACTIVE",
    },
    "implemented": {
        "light_bg": "#E8F6EE",
        "light_text": "#18794E",
        "light_border": "#C2EBD4",
        "dark_bg": "rgba(34, 197, 94, 0.15)",
        "dark_text": "#4ADE80",
        "dark_border": "rgba(74, 222, 128, 0.35)",
        "label": "IMPLEMENTED",
    },
    "planned": {
        "light_bg": "#EAF2FF",
        "light_text": "#245AC7",
        "light_border": "#C3D7FA",
        "dark_bg": "rgba(56, 189, 248, 0.15)",
        "dark_text": "#38BDF8",
        "dark_border": "rgba(56, 189, 248, 0.35)",
        "label": "PLANNED",
    },
    "reconsider": {
        "light_bg": "#FFF4DE",
        "light_text": "#A85B08",
        "light_border": "#FDE3B2",
        "dark_bg": "rgba(245, 158, 11, 0.15)",
        "dark_text": "#FBBF24",
        "dark_border": "rgba(251, 191, 36, 0.35)",
        "label": "RECONSIDER",
    },
    "rejected": {
        "light_bg": "#FDECEE",
        "light_text": "#B42332",
        "light_border": "#F9CCD1",
        "dark_bg": "rgba(239, 68, 68, 0.15)",
        "dark_text": "#F87171",
        "dark_border": "rgba(248, 113, 113, 0.35)",
        "label": "REJECTED",
    },
    "on_hold": {
        "light_bg": "#FFF4DE",
        "light_text": "#A85B08",
        "light_border": "#FDE3B2",
        "dark_bg": "rgba(245, 158, 11, 0.15)",
        "dark_text": "#FBBF24",
        "dark_border": "rgba(251, 191, 36, 0.35)",
        "label": "ON HOLD",
    },
    "completed": {
        "light_bg": "#E6F7F5",
        "light_text": "#087F8C",
        "light_border": "#B0EBE4",
        "dark_bg": "rgba(20, 184, 166, 0.15)",
        "dark_text": "#5EEAD4",
        "dark_border": "rgba(94, 234, 212, 0.35)",
        "label": "COMPLETED",
    },
    "revisited": {
        "light_bg": "#F3EFFF",
        "light_text": "#7958D8",
        "light_border": "#DFD5FA",
        "dark_bg": "rgba(99, 102, 241, 0.15)",
        "dark_text": "#818CF8",
        "dark_border": "rgba(129, 140, 248, 0.35)",
        "label": "REVISITED",
    },
    "superseded": {
        "light_bg": "#FFF4DE",
        "light_text": "#A85B08",
        "light_border": "#FDE3B2",
        "dark_bg": "rgba(249, 115, 22, 0.15)",
        "dark_text": "#FB923C",
        "dark_border": "rgba(251, 146, 60, 0.35)",
        "label": "SUPERSEDED",
    },
    "reconsidered": {
        "light_bg": "#EAF2FF",
        "light_text": "#245AC7",
        "light_border": "#C3D7FA",
        "dark_bg": "rgba(59, 130, 246, 0.15)",
        "dark_text": "#60A5FA",
        "dark_border": "rgba(96, 165, 250, 0.35)",
        "label": "RECONSIDERED",
    },
}


def get_current_theme() -> str:
    """Return the active user theme: 'light', 'dark', or 'system'."""
    return st.session_state.get("theme", "light")


def set_current_theme(theme_name: str) -> None:
    """Set the active theme preference ('light', 'dark', 'system') across all synced keys."""
    if theme_name in ["light", "dark", "system"]:
        st.session_state["theme"] = theme_name
        st.session_state["app_theme_radio_sidebar"] = theme_name
        if "settings_theme_radio" in st.session_state:
            st.session_state["settings_theme_radio"] = theme_name


def badge_html(category: str, value: str) -> str:
    """Return sleek styled HTML badge with theme-aware borders and typography."""
    lookup = {
        "epistemic": EPISTEMIC_COLORS,
        "drift": DRIFT_COLORS,
        "comparison": COMPARISON_COLORS,
        "causal": CAUSAL_COLORS,
        "status": STATUS_COLORS,
    }
    c_map = lookup.get(category, {})
    val_key = value.lower().replace(" ", "_") if value else ""
    colors = c_map.get(
        val_key,
        {
            "light_bg": "#EEF2F8",
            "light_text": "#52627A",
            "light_border": "#DCE3ED",
            "dark_bg": "rgba(100, 116, 139, 0.2)",
            "dark_text": "#94A3B8",
            "dark_border": "rgba(148, 163, 184, 0.3)",
            "label": value.upper() if value else "",
        },
    )

    label = colors.get("label", "")
    if not label:
        return ""

    theme = get_current_theme()
    is_dark = theme == "dark"

    bg = colors["dark_bg"] if is_dark else colors["light_bg"]
    text_c = colors["dark_text"] if is_dark else colors["light_text"]
    border_c = colors["dark_border"] if is_dark else colors["light_border"]

    glow = f"box-shadow: 0 0 10px {border_c}40;" if "explicit" in val_key or "high" in val_key else ""
    return (
        f'<span class="dp-badge" style="background:{bg}; color:{text_c}; '
        f'border: 1px solid {border_c}; {glow}">{label}</span>'
    )


def inject_custom_css() -> None:
    """Inject light-first enterprise SaaS CSS with full dark and system mode support."""
    theme = get_current_theme()

    # CSS Token Variables
    if theme == "dark":
        theme_vars = """
        --dp-bg-app: #0B0F19;
        --dp-bg-main: #0B0F19;
        --dp-surface-card: #111827;
        --dp-surface-secondary: #1E293B;
        --dp-sidebar-bg: #0C1220;
        --dp-sidebar-surface: #111827;
        --dp-sidebar-text: #F8FAFC;
        --dp-sidebar-border: #1E293B;
        --dp-text-primary: #F8FAFC;
        --dp-text-secondary: #94A3B8;
        --dp-text-muted: #64748B;
        --dp-primary: #3B82F6;
        --dp-primary-hover: #60A5FA;
        --dp-primary-light: rgba(59, 130, 246, 0.15);
        --dp-border: #1E293B;
        --dp-border-strong: #334155;
        --dp-card-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.5);
        --dp-table-hover: rgba(255, 255, 255, 0.03);
        --dp-input-bg: #131C2E;
        --dp-input-border: #334155;
        --dp-input-text: #F8FAFC;
        --dp-success: #34D399;
        --dp-success-bg: rgba(16, 185, 129, 0.15);
        --dp-error: #F87171;
        --dp-error-bg: rgba(239, 68, 68, 0.18);
        --dp-warning: #FBBF24;
        --dp-warning-bg: rgba(245, 158, 11, 0.15);
        --dp-info: #60A5FA;
        --dp-info-bg: rgba(59, 130, 246, 0.15);
        """
    elif theme == "system":
        theme_vars = """
        --dp-bg-app: #F8FAFC;
        --dp-bg-main: #F8FAFC;
        --dp-surface-card: #FFFFFF;
        --dp-surface-secondary: #F1F5F9;
        --dp-sidebar-bg: #FFFFFF;
        --dp-sidebar-surface: #F8FAFC;
        --dp-sidebar-text: #0F172A;
        --dp-sidebar-border: #E2E8F0;
        --dp-text-primary: #0F172A;
        --dp-text-secondary: #475569;
        --dp-text-muted: #64748B;
        --dp-primary: #2563EB;
        --dp-primary-hover: #1D4ED8;
        --dp-primary-light: #EFF6FF;
        --dp-border: #E2E8F0;
        --dp-border-strong: #CBD5E1;
        --dp-card-shadow: 0 1px 3px rgba(15, 23, 42, 0.05), 0 4px 12px rgba(15, 23, 42, 0.03);
        --dp-table-hover: #F8FAFD;
        --dp-input-bg: #FFFFFF;
        --dp-input-border: #CBD5E1;
        --dp-input-text: #0F172A;
        --dp-success: #16A34A;
        --dp-success-bg: #F0FDF4;
        --dp-error: #DC2626;
        --dp-error-bg: #FEF2F2;
        --dp-warning: #D97706;
        --dp-warning-bg: #FFFBEB;
        --dp-info: #2563EB;
        --dp-info-bg: #EFF6FF;
        @media (prefers-color-scheme: dark) {
            --dp-bg-app: #0B0F19;
            --dp-bg-main: #0B0F19;
            --dp-surface-card: #111827;
            --dp-surface-secondary: #1E293B;
            --dp-sidebar-bg: #0C1220;
            --dp-sidebar-surface: #111827;
            --dp-sidebar-text: #F8FAFC;
            --dp-sidebar-border: #1E293B;
            --dp-text-primary: #F8FAFC;
            --dp-text-secondary: #94A3B8;
            --dp-text-muted: #64748B;
            --dp-primary: #3B82F6;
            --dp-primary-hover: #60A5FA;
            --dp-primary-light: rgba(59, 130, 246, 0.15);
            --dp-border: #1E293B;
            --dp-border-strong: #334155;
            --dp-card-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.5);
            --dp-table-hover: rgba(255, 255, 255, 0.03);
            --dp-input-bg: #131C2E;
            --dp-input-border: #334155;
            --dp-input-text: #F8FAFC;
            --dp-success: #34D399;
            --dp-success-bg: rgba(16, 185, 129, 0.15);
            --dp-error: #F87171;
            --dp-error-bg: rgba(239, 68, 68, 0.18);
            --dp-warning: #FBBF24;
            --dp-warning-bg: rgba(245, 158, 11, 0.15);
            --dp-info: #60A5FA;
            --dp-info-bg: rgba(59, 130, 246, 0.15);
        }
        """
    else:  # light (default)
        theme_vars = """
        --dp-bg-app: #F8FAFC;
        --dp-bg-main: #F8FAFC;
        --dp-surface-card: #FFFFFF;
        --dp-surface-secondary: #F1F5F9;
        --dp-sidebar-bg: #FFFFFF;
        --dp-sidebar-surface: #F8FAFC;
        --dp-sidebar-text: #0F172A;
        --dp-sidebar-border: #E2E8F0;
        --dp-text-primary: #0F172A;
        --dp-text-secondary: #475569;
        --dp-text-muted: #64748B;
        --dp-primary: #2563EB;
        --dp-primary-hover: #1D4ED8;
        --dp-primary-light: #EFF6FF;
        --dp-border: #E2E8F0;
        --dp-border-strong: #CBD5E1;
        --dp-card-shadow: 0 1px 3px rgba(15, 23, 42, 0.05), 0 4px 12px rgba(15, 23, 42, 0.03);
        --dp-table-hover: #F8FAFD;
        --dp-input-bg: #FFFFFF;
        --dp-input-border: #CBD5E1;
        --dp-input-text: #0F172A;
        --dp-success: #16A34A;
        --dp-success-bg: #F0FDF4;
        --dp-error: #DC2626;
        --dp-error-bg: #FEF2F2;
        --dp-warning: #D97706;
        --dp-warning-bg: #FFFBEB;
        --dp-info: #2563EB;
        --dp-info-bg: #EFF6FF;
        """

    st.markdown(
        f"""
<style>
/* =========================================================================
   DECISIONPRINT ENTERPRISE SAAS DESIGN SYSTEM
   Exact Light-First Reference with Dark/System Options
   ========================================================================= */

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {{
    {theme_vars}
    --dp-violet: #7958D8;
    --dp-teal: #087F8C;
    --dp-focus-ring: var(--dp-primary);
}}

/* --- Root & App Canvas --- */
.stApp {{
    background-color: var(--dp-bg-app) !important;
    color: var(--dp-text-primary) !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
    letter-spacing: -0.01em;
}}

/* --- Typography --- */
h1, h2, h3, h4, h5, h6 {{
    font-family: 'Inter', sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: -0.025em !important;
    color: var(--dp-text-primary) !important;
}}

h1 {{ font-size: 2rem !important; margin-bottom: 0.25rem !important; }}
h2 {{ font-size: 1.55rem !important; }}
h3 {{ font-size: 1.25rem !important; }}
h4 {{ font-size: 1.05rem !important; }}

p, span, label, div {{
    color: var(--dp-text-primary);
}}

/* Custom Scrollbar */
::-webkit-scrollbar {{
    width: 6px;
    height: 6px;
}}
::-webkit-scrollbar-track {{
    background: var(--dp-bg-app);
}}
::-webkit-scrollbar-thumb {{
    background: var(--dp-border-strong);
    border-radius: 4px;
}}
::-webkit-scrollbar-thumb:hover {{
    background: var(--dp-primary);
}}

/* --- Enterprise Sidebar (Cohesive with active theme) --- */
[data-testid="stSidebar"] {{
    background-color: var(--dp-sidebar-bg) !important;
    border-right: 1px solid var(--dp-sidebar-border) !important;
}}

[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span:not(.dp-badge),
[data-testid="stSidebar"] label {{
    color: var(--dp-sidebar-text) !important;
}}

[data-testid="stSidebarNav"] a {{
    background: transparent !important;
    border-radius: 8px !important;
    margin: 2px 8px !important;
    padding: 8px 12px !important;
    font-weight: 500 !important;
    color: var(--dp-sidebar-text) !important;
    transition: all 0.15s ease !important;
}}

[data-testid="stSidebarNav"] a span {{
    color: var(--dp-sidebar-text) !important;
    font-weight: 500 !important;
    transition: color 0.15s ease !important;
}}

[data-testid="stSidebarNav"] a:hover {{
    background: var(--dp-surface-secondary) !important;
}}

[data-testid="stSidebarNav"] a:hover span {{
    color: var(--dp-primary) !important;
}}

[data-testid="stSidebarNav"] a[aria-current="page"] {{
    background: var(--dp-primary-light) !important;
    border-left: 3px solid var(--dp-primary) !important;
}}

[data-testid="stSidebarNav"] a[aria-current="page"] span {{
    color: var(--dp-primary) !important;
    font-weight: 700 !important;
}}

.dp-sidebar-header {{
    padding: 0.5rem 0.5rem 0.8rem 0.5rem;
}}

.dp-sidebar-logo-group {{
    display: flex;
    align-items: center;
    gap: 0.75rem;
}}

.dp-sidebar-brand-name {{
    font-size: 1.25rem;
    font-weight: 800;
    color: var(--dp-sidebar-text) !important;
    letter-spacing: -0.03em;
}}

.dp-sidebar-brand-sub {{
    font-size: 0.72rem;
    color: var(--dp-primary) !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-weight: 600;
}}

.dp-sidebar-divider {{
    height: 1px;
    background: var(--dp-sidebar-border);
    margin: 1rem 0;
}}

.dp-sidebar-status-card {{
    background: var(--dp-sidebar-surface) !important;
    border: 1px solid var(--dp-sidebar-border) !important;
    border-radius: 8px;
    padding: 0.65rem 0.85rem;
    margin-top: 1rem;
}}

.dp-sidebar-status-pill {{
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.75rem;
    color: var(--dp-sidebar-text) !important;
    font-family: 'JetBrains Mono', monospace;
}}

.dp-status-dot {{
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--dp-success);
    box-shadow: 0 0 8px var(--dp-success);
    display: inline-block;
}}

.dp-sidebar-status-detail {{
    display: flex;
    align-items: center;
    gap: 0.4rem;
    font-size: 0.75rem;
    color: var(--dp-text-muted) !important;
    margin-top: 0.35rem;
}}

.dp-sidebar-user-card {{
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.75rem;
    background: var(--dp-sidebar-surface) !important;
    border: 1px solid var(--dp-sidebar-border) !important;
    border-radius: 10px;
    margin-top: 1.5rem;
}}

.dp-user-avatar-lg {{
    width: 38px;
    height: 38px;
    border-radius: 50%;
    background: linear-gradient(135deg, var(--dp-primary), var(--dp-violet));
    color: #FFFFFF !important;
    font-weight: 700;
    font-size: 0.88rem;
    display: flex;
    align-items: center;
    justify-content: center;
}}

.dp-user-name {{
    font-weight: 600;
    font-size: 0.88rem;
    color: var(--dp-sidebar-text) !important;
}}

.dp-user-role {{
    font-size: 0.75rem;
    color: var(--dp-text-muted) !important;
}}

.dp-sidebar-version {{
    font-size: 0.7rem;
    color: var(--dp-text-muted) !important;
    font-family: 'JetBrains Mono', monospace;
    text-align: center;
    margin-top: 0.75rem;
}}

/* --- Top Application Bar --- */
.dp-topbar {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: var(--dp-surface-card);
    border: 1px solid var(--dp-border);
    border-radius: 12px;
    padding: 0.65rem 1.25rem;
    margin-bottom: 1.5rem;
    box-shadow: var(--dp-card-shadow);
}}

.dp-topbar-left {{
    display: flex;
    align-items: center;
}}

.dp-topbar-brand {{
    display: flex;
    align-items: center;
    gap: 0.6rem;
}}

.dp-topbar-title {{
    font-size: 1.15rem;
    font-weight: 700;
    color: var(--dp-text-primary);
    letter-spacing: -0.02em;
}}

.dp-topbar-tagline {{
    font-size: 0.82rem;
    color: var(--dp-text-muted);
    margin-left: 0.6rem;
    border-left: 1px solid var(--dp-border);
    padding-left: 0.6rem;
}}

.dp-topbar-center {{
    flex: 1;
    display: flex;
    justify-content: center;
    padding: 0 1.5rem;
}}

.dp-topbar-search {{
    display: flex;
    align-items: center;
    gap: 0.6rem;
    background: var(--dp-bg-app);
    border: 1px solid var(--dp-border);
    border-radius: 8px;
    padding: 0.45rem 1rem;
    width: 100%;
    max-width: 440px;
    font-size: 0.85rem;
    color: var(--dp-text-muted);
    transition: all 0.2s ease;
}}

.dp-topbar-search:hover {{
    border-color: var(--dp-primary);
}}

.dp-search-placeholder {{
    color: var(--dp-text-muted);
    font-size: 0.82rem;
}}

.dp-topbar-right {{
    display: flex;
    align-items: center;
    gap: 1rem;
}}

.dp-breadcrumbs {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.74rem;
    letter-spacing: 0.08em;
}}

.dp-breadcrumb-active {{
    color: var(--dp-primary);
    font-weight: 700;
}}

.dp-breadcrumb-idle {{
    color: var(--dp-text-muted);
}}

.dp-breadcrumb-sep {{
    color: var(--dp-border-strong);
    margin: 0 0.35rem;
}}

.dp-topbar-actions {{
    display: flex;
    align-items: center;
    gap: 0.6rem;
}}

.dp-icon-btn {{
    width: 32px;
    height: 32px;
    border-radius: 8px;
    background: var(--dp-bg-app);
    border: 1px solid var(--dp-border);
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.2s ease;
}}

.dp-icon-btn:hover {{
    background: var(--dp-primary-light);
    border-color: var(--dp-primary);
}}

.dp-user-avatar {{
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: linear-gradient(135deg, #315EDE, #7958D8);
    color: #FFFFFF !important;
    font-weight: 700;
    font-size: 0.78rem;
    display: flex;
    align-items: center;
    justify-content: center;
    border: 1.5px solid var(--dp-border);
}}

/* --- Theme Switcher Segmented Control --- */
.dp-theme-picker {{
    display: inline-flex;
    align-items: center;
    background: var(--dp-bg-app);
    border: 1px solid var(--dp-border);
    border-radius: 8px;
    padding: 2px;
    gap: 2px;
}}

.dp-theme-opt {{
    padding: 3px 8px;
    border-radius: 6px;
    font-size: 0.75rem;
    font-weight: 600;
    color: var(--dp-text-secondary);
    cursor: pointer;
    text-decoration: none;
    transition: all 0.15s ease;
}}

.dp-theme-opt.active {{
    background: var(--dp-surface-card);
    color: var(--dp-primary);
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}}

/* --- Enterprise Cards (Crisp Elevated Surface) --- */
.dp-card {{
    background: var(--dp-surface-card) !important;
    border: 1px solid var(--dp-border) !important;
    border-radius: 12px !important;
    padding: 1.35rem 1.5rem !important;
    margin-bottom: 1.25rem !important;
    box-shadow: var(--dp-card-shadow) !important;
    transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
}}

.dp-card:hover {{
    border-color: var(--dp-border-strong) !important;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.07) !important;
}}

/* --- Responsive 6-KPI Row --- */
.dp-kpi-card {{
    background: var(--dp-surface-card);
    border: 1px solid var(--dp-border);
    border-radius: 12px;
    padding: 1rem 1.15rem;
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
    box-shadow: var(--dp-card-shadow);
    transition: all 0.2s ease;
}}

.dp-kpi-card:hover {{
    border-color: var(--dp-primary);
    transform: translateY(-2px);
}}

.dp-kpi-label {{
    font-size: 0.8rem;
    color: var(--dp-text-secondary);
    font-weight: 500;
}}

.dp-kpi-value {{
    font-size: 1.75rem;
    font-weight: 700;
    color: var(--dp-text-primary);
    letter-spacing: -0.03em;
    line-height: 1.2;
}}

.dp-kpi-trend-pos {{
    font-size: 0.72rem;
    color: var(--dp-success);
    font-family: 'JetBrains Mono', monospace;
    font-weight: 600;
}}

.dp-kpi-trend-neg {{
    font-size: 0.72rem;
    color: var(--dp-error);
    font-family: 'JetBrains Mono', monospace;
    font-weight: 600;
}}

/* --- Activity Feed Items --- */
.dp-activity-item {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.75rem 0;
    border-bottom: 1px solid var(--dp-border);
}}

.dp-activity-item:last-child {{
    border-bottom: none;
}}

.dp-activity-title {{
    font-size: 0.88rem;
    font-weight: 600;
    color: var(--dp-text-primary);
}}

.dp-activity-sub {{
    font-size: 0.78rem;
    color: var(--dp-text-muted);
    margin-top: 0.15rem;
}}

/* --- Drift Alert Card --- */
.dp-drift-alert-box {{
    background: var(--dp-error-bg);
    border: 1px solid #F9CCD1;
    border-radius: 12px;
    padding: 1.25rem 1.4rem;
}}

.dp-drift-alert-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.5rem;
}}

.dp-drift-alert-title {{
    font-size: 1.02rem;
    font-weight: 700;
    color: var(--dp-error);
}}

.dp-drift-alert-desc {{
    font-size: 0.85rem;
    color: var(--dp-text-secondary);
    line-height: 1.5;
    margin-bottom: 0.8rem;
}}

/* --- System Health Card --- */
.dp-health-box {{
    background: var(--dp-surface-card);
    border: 1px solid var(--dp-border);
    border-radius: 12px;
    padding: 1.1rem 1.25rem;
    margin-top: 1rem;
    box-shadow: var(--dp-card-shadow);
}}

.dp-health-status {{
    display: flex;
    align-items: center;
    gap: 0.6rem;
    font-size: 0.88rem;
    font-weight: 600;
    color: var(--dp-success);
    margin-top: 0.3rem;
}}

.dp-pulse-dot {{
    width: 9px;
    height: 9px;
    border-radius: 50%;
    background: var(--dp-success);
    box-shadow: 0 0 10px var(--dp-success);
    animation: dpPulse 2s infinite ease-in-out;
}}

@keyframes dpPulse {{
    0% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(24, 121, 78, 0.7); }}
    70% {{ transform: scale(1.05); box-shadow: 0 0 0 8px rgba(24, 121, 78, 0); }}
    100% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(24, 121, 78, 0); }}
}}

/* --- Badges & Micro-tags --- */
.dp-badge {{
    display: inline-flex !important;
    align-items: center !important;
    padding: 3px 10px !important;
    border-radius: 9999px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.74rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.04em !important;
    text-transform: uppercase !important;
    white-space: nowrap !important;
    margin-right: 0.4rem !important;
}}

.dp-badge-review {{
    background: var(--dp-error-bg) !important;
    color: var(--dp-error) !important;
    border: 1px solid #F9CCD1 !important;
}}

/* --- Suggested Questions Pills --- */
.dp-pill-container {{
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin: 0.75rem 0 1.25rem 0;
}}

.dp-suggested-pill {{
    background: var(--dp-bg-app);
    border: 1px solid var(--dp-border);
    color: var(--dp-text-secondary);
    border-radius: 9999px;
    padding: 0.35rem 0.85rem;
    font-size: 0.8rem;
    cursor: pointer;
    transition: all 0.2s ease;
}}

.dp-suggested-pill:hover {{
    border-color: var(--dp-primary);
    color: var(--dp-primary);
    background: var(--dp-primary-light);
}}

/* --- Data Tables --- */
.dp-table {{
    width: 100%;
    border-collapse: collapse;
    margin: 1rem 0;
    font-size: 0.88rem;
}}

.dp-table th {{
    text-align: left;
    padding: 0.75rem 1rem;
    color: var(--dp-text-muted);
    font-weight: 600;
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    border-bottom: 1px solid var(--dp-border-strong);
}}

.dp-table td {{
    padding: 0.85rem 1rem;
    border-bottom: 1px solid var(--dp-border);
    color: var(--dp-text-primary);
}}

.dp-table tr:hover td {{
    background-color: var(--dp-table-hover);
}}

/* --- Code & Inline Syntax --- */
code {{
    background-color: var(--dp-surface-secondary) !important;
    color: var(--dp-primary) !important;
    border: 1px solid var(--dp-border) !important;
    padding: 0.15rem 0.4rem !important;
    border-radius: 6px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.85em !important;
}}

hr, .dp-sidebar-divider {{
    border: none !important;
    height: 1px !important;
    background-color: var(--dp-border) !important;
    margin: 1rem 0 !important;
}}

/* --- Container Wrappers --- */
[data-testid="stVerticalBlockBorderWrapper"] {{
    background-color: var(--dp-surface-card) !important;
    border: 1px solid var(--dp-border) !important;
    border-radius: 12px !important;
    box-shadow: var(--dp-card-shadow) !important;
}}

/* --- Primary & Secondary Action Buttons --- */
.stButton > button {{
    border-radius: 8px !important;
    padding: 0.45rem 1.15rem !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    transition: all 0.15s ease !important;
}}

/* Primary Buttons */
.stButton > button[kind="primary"],
.stButton > button[data-testid="baseButton-primary"] {{
    background: var(--dp-primary) !important;
    color: #FFFFFF !important;
    border: 1px solid var(--dp-primary) !important;
    box-shadow: 0 1px 3px rgba(37, 99, 235, 0.25) !important;
}}

.stButton > button[kind="primary"]:hover,
.stButton > button[data-testid="baseButton-primary"]:hover {{
    background: var(--dp-primary-hover) !important;
    border-color: var(--dp-primary-hover) !important;
    color: #FFFFFF !important;
    transform: translateY(-1px) !important;
}}

/* Secondary / Standard Buttons (Chips & Cards) */
.stButton > button[kind="secondary"],
.stButton > button[data-testid="baseButton-secondary"],
.stButton > button:not([kind="primary"]):not([data-testid="baseButton-primary"]) {{
    background: var(--dp-surface-card) !important;
    color: var(--dp-text-primary) !important;
    border: 1px solid var(--dp-border-strong) !important;
    box-shadow: var(--dp-card-shadow) !important;
}}

.stButton > button[kind="secondary"]:hover,
.stButton > button[data-testid="baseButton-secondary"]:hover,
.stButton > button:not([kind="primary"]):not([data-testid="baseButton-primary"]):hover {{
    background: var(--dp-surface-secondary) !important;
    border-color: var(--dp-primary) !important;
    color: var(--dp-primary) !important;
    transform: translateY(-1px) !important;
}}

/* --- Form Controls & Text Inputs --- */
[data-baseweb="input"],
[data-baseweb="base-input"],
[data-baseweb="select"],
.stTextInput > div > div,
.stTextArea > div > div {{
    background-color: var(--dp-input-bg) !important;
    border: 1px solid var(--dp-input-border) !important;
    border-radius: 8px !important;
    color: var(--dp-input-text) !important;
    transition: all 0.2s ease !important;
}}

[data-baseweb="select"] > div {{
    background-color: var(--dp-input-bg) !important;
    border: 1px solid var(--dp-input-border) !important;
    border-radius: 8px !important;
    color: var(--dp-input-text) !important;
}}

[data-baseweb="input"]:focus-within,
[data-baseweb="select"] > div:focus-within,
.stTextInput > div > div:focus-within {{
    border-color: var(--dp-primary) !important;
    box-shadow: 0 0 0 2px var(--dp-primary-light) !important;
}}

/* Real <input> and <textarea> text visibility & typing capability */
input,
textarea,
[data-baseweb="input"] input,
[data-baseweb="base-input"] input,
[data-baseweb="textarea"] textarea,
.stTextInput input,
.stTextArea textarea {{
    background-color: transparent !important;
    color: var(--dp-input-text) !important;
    -webkit-text-fill-color: var(--dp-input-text) !important;
    caret-color: var(--dp-primary) !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    font-size: 0.9rem !important;
    opacity: 1 !important;
    pointer-events: auto !important;
}}

input::placeholder,
textarea::placeholder,
.stTextInput input::placeholder,
.stTextArea textarea::placeholder {{
    color: var(--dp-text-muted) !important;
    -webkit-text-fill-color: var(--dp-text-muted) !important;
    opacity: 0.75 !important;
}}

/* Dropdown Menu & Popovers */
[data-baseweb="select"] * {{
    color: var(--dp-text-primary) !important;
    -webkit-text-fill-color: var(--dp-text-primary) !important;
}}

div[data-baseweb="popover"],
div[data-baseweb="menu"],
ul[role="listbox"],
li[role="option"] {{
    background-color: var(--dp-surface-card) !important;
    border-color: var(--dp-border) !important;
    color: var(--dp-text-primary) !important;
}}

li[role="option"]:hover,
li[role="option"][aria-selected="true"] {{
    background-color: var(--dp-primary-light) !important;
    color: var(--dp-primary) !important;
}}

/* Sidebar Select & Input styling */
[data-testid="stSidebar"] [data-baseweb="select"],
[data-testid="stSidebar"] [data-baseweb="input"] {{
    background-color: var(--dp-sidebar-surface) !important;
    border: 1px solid var(--dp-sidebar-border) !important;
}}

[data-testid="stSidebar"] [data-baseweb="select"] *,
[data-testid="stSidebar"] input {{
    color: var(--dp-sidebar-text) !important;
    -webkit-text-fill-color: var(--dp-sidebar-text) !important;
}}

/* Radio buttons & Checkboxes */
[data-testid="stRadio"] label,
[data-testid="stCheckbox"] label {{
    color: var(--dp-text-primary) !important;
    font-weight: 500 !important;
}}

[data-testid="stSidebar"] [data-testid="stRadio"] label,
[data-testid="stSidebar"] [data-testid="stCheckbox"] label {{
    color: var(--dp-sidebar-text) !important;
}}

/* --- Tabs --- */
[data-testid="stTabs"] {{
    background: transparent;
    border-bottom: 1px solid var(--dp-border);
}}

[data-testid="stTabs"] [data-baseweb="tab"] {{
    background: transparent !important;
    border-radius: 8px 8px 0 0 !important;
    color: var(--dp-text-muted) !important;
    font-weight: 600 !important;
    padding: 0.6rem 1.2rem !important;
    border: none !important;
}}

[data-testid="stTabs"] [aria-selected="true"] {{
    color: var(--dp-primary) !important;
    border-bottom: 2px solid var(--dp-primary) !important;
}}

/* --- Modals & Dialogs --- */
[data-testid="stDialog"] div[role="dialog"] {{
    background: var(--dp-surface-card) !important;
    border: 1px solid var(--dp-border-strong) !important;
    border-radius: 16px !important;
    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.25) !important;
}}

/* --- Timeline Nodes --- */
.dp-timeline-item {{
    position: relative;
    padding-left: 2.2rem;
    padding-bottom: 1.6rem;
    border-left: 2px solid var(--dp-border-strong);
}}

.dp-timeline-item:last-child {{
    border-left: 2px solid transparent;
}}

.dp-timeline-dot {{
    position: absolute;
    left: -7px;
    top: 4px;
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background: var(--dp-primary);
    box-shadow: 0 0 8px var(--dp-primary);
}}

.dp-timeline-date {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem;
    color: var(--dp-text-muted);
    margin-bottom: 0.3rem;
}}

.dp-chain-arrow {{
    font-size: 1.4rem;
    color: var(--dp-primary);
    text-align: center;
    margin: 0.5rem 0;
}}
</style>
    """,
        unsafe_allow_html=True,
    )
