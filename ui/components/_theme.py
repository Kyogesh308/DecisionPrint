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
    "inject_theme",
    "set_current_theme",
]

# Epistemic types (Fact=blue, Observation=teal, Inference=yellow, Recommendation=ink pill)
EPISTEMIC_COLORS = {
    "fact": {
        "light_bg": "#EBF2FE",
        "light_text": "#1A4BA8",
        "light_border": "#5B8DEF",
        "dark_bg": "rgba(91, 141, 239, 0.2)",
        "dark_text": "#5B8DEF",
        "dark_border": "#5B8DEF",
        "label": "FACT",
    },
    "observation": {
        "light_bg": "#EAF8F8",
        "light_text": "#0B6A68",
        "light_border": "#52C4C0",
        "dark_bg": "rgba(82, 196, 192, 0.2)",
        "dark_text": "#52C4C0",
        "dark_border": "#52C4C0",
        "label": "OBSERVATION",
    },
    "inference": {
        "light_bg": "#FFF9E6",
        "light_text": "#111111",
        "light_border": "#FFC43D",
        "dark_bg": "rgba(255, 196, 61, 0.2)",
        "dark_text": "#FFC43D",
        "dark_border": "#FFC43D",
        "label": "INFERENCE",
    },
    "recommendation": {
        "light_bg": "#111111",
        "light_text": "#FFFFFF",
        "light_border": "#111111",
        "dark_bg": "#EEEEEE",
        "dark_text": "#111111",
        "dark_border": "#EEEEEE",
        "label": "RECOMMENDATION",
    },
}

# Drift levels (none=teal, low=yellow, medium=coral-tint, high=solid coral)
DRIFT_COLORS = {
    "none": {
        "light_bg": "#EAF8F8",
        "light_text": "#0B6A68",
        "light_border": "#52C4C0",
        "dark_bg": "rgba(82, 196, 192, 0.2)",
        "dark_text": "#52C4C0",
        "dark_border": "#52C4C0",
        "bg": "#EAF8F8",
        "text": "#0B6A68",
        "border": "#52C4C0",
        "label": "NO DRIFT",
    },
    "low": {
        "light_bg": "#FFF9E6",
        "light_text": "#111111",
        "light_border": "#FFC43D",
        "dark_bg": "rgba(255, 196, 61, 0.2)",
        "dark_text": "#FFC43D",
        "dark_border": "#FFC43D",
        "bg": "#FFF9E6",
        "text": "#111111",
        "border": "#FFC43D",
        "label": "LOW DRIFT",
    },
    "medium": {
        "light_bg": "#FDDCD6",
        "light_text": "#111111",
        "light_border": "#F26F55",
        "dark_bg": "rgba(242, 111, 85, 0.2)",
        "dark_text": "#F26F55",
        "dark_border": "#F26F55",
        "bg": "#FDDCD6",
        "text": "#111111",
        "border": "#F26F55",
        "label": "MEDIUM DRIFT",
    },
    "high": {
        "light_bg": "#F26F55",
        "light_text": "#FFFFFF",
        "light_border": "#111111",
        "dark_bg": "#F26F55",
        "dark_text": "#FFFFFF",
        "dark_border": "#EEEEEE",
        "bg": "#F26F55",
        "text": "#FFFFFF",
        "border": "#111111",
        "label": "HIGH DRIFT",
    },
}

# Comparison badges (same=grey, changed=coral, newly_present=yellow, unknown=dashed grey, incomparable=struck grey)
COMPARISON_COLORS = {
    "same": {
        "light_bg": "#F0F0F0",
        "light_text": "#8A8A8A",
        "light_border": "#8A8A8A",
        "dark_bg": "rgba(138, 138, 138, 0.15)",
        "dark_text": "#8A8A8A",
        "dark_border": "#8A8A8A",
        "label": "UNCHANGED",
    },
    "changed": {
        "light_bg": "#FDDCD6",
        "light_text": "#C23E25",
        "light_border": "#F26F55",
        "dark_bg": "rgba(242, 111, 85, 0.25)",
        "dark_text": "#F26F55",
        "dark_border": "#F26F55",
        "label": "CHANGED",
    },
    "newly_present": {
        "light_bg": "#FFF9E6",
        "light_text": "#111111",
        "light_border": "#FFC43D",
        "dark_bg": "rgba(255, 196, 61, 0.2)",
        "dark_text": "#FFC43D",
        "dark_border": "#FFC43D",
        "label": "NEW",
    },
    "unknown": {
        "light_bg": "#F0F0F0",
        "light_text": "#8A8A8A",
        "light_border": "#8A8A8A",
        "border_style": "dashed",
        "dark_bg": "rgba(138, 138, 138, 0.15)",
        "dark_text": "#8A8A8A",
        "dark_border": "#8A8A8A",
        "label": "UNKNOWN",
    },
    "incomparable": {
        "light_bg": "#F0F0F0",
        "light_text": "#8A8A8A",
        "light_border": "#8A8A8A",
        "text_decoration": "line-through",
        "dark_bg": "rgba(138, 138, 138, 0.15)",
        "dark_text": "#8A8A8A",
        "dark_border": "#8A8A8A",
        "label": "INCOMPARABLE",
    },
}

# Causal link labels (explicit_causal_link=blue fill + ink outline, strong=teal, possible=yellow, fact=blue, none=never render)
CAUSAL_COLORS = {
    "explicit_causal_link": {
        "light_bg": "#5B8DEF",
        "light_text": "#FFFFFF",
        "light_border": "#111111",
        "dark_bg": "#5B8DEF",
        "dark_text": "#FFFFFF",
        "dark_border": "#EEEEEE",
        "label": "EXPLICIT CAUSAL LINK",
    },
    "strong_evidence": {
        "light_bg": "#52C4C0",
        "light_text": "#111111",
        "light_border": "#111111",
        "dark_bg": "#52C4C0",
        "dark_text": "#111111",
        "dark_border": "#EEEEEE",
        "label": "STRONG EVIDENCE",
    },
    "possible_causal_link": {
        "light_bg": "#FFC43D",
        "light_text": "#111111",
        "light_border": "#111111",
        "dark_bg": "#FFC43D",
        "dark_text": "#111111",
        "dark_border": "#EEEEEE",
        "label": "POSSIBLE LINK",
    },
    "fact": {
        "light_bg": "#5B8DEF",
        "light_text": "#FFFFFF",
        "light_border": "#111111",
        "dark_bg": "#5B8DEF",
        "dark_text": "#FFFFFF",
        "dark_border": "#EEEEEE",
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
    """Return sleek soft neo-brutalist styled HTML badge with theme-aware borders and typography."""
    if category == "causal" and (not value or str(value).lower() in ("none", "")):
        return ""

    lookup = {
        "epistemic": EPISTEMIC_COLORS,
        "drift": DRIFT_COLORS,
        "comparison": COMPARISON_COLORS,
        "causal": CAUSAL_COLORS,
        "status": STATUS_COLORS,
    }
    c_map = lookup.get(category, {})
    val_key = value.lower().replace(" ", "_") if value else ""
    if category == "causal" and val_key == "none":
        return ""

    colors = c_map.get(
        val_key,
        {
            "light_bg": "#F0F0F0",
            "light_text": "#111111",
            "light_border": "#111111",
            "dark_bg": "rgba(255, 255, 255, 0.1)",
            "dark_text": "#EEEEEE",
            "dark_border": "#EEEEEE",
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

    border_style = colors.get("border_style", "solid")
    text_dec = f"text-decoration: {colors['text_decoration']};" if "text_decoration" in colors else ""
    thick_edge = (
        "border-bottom: 2.5px solid var(--ink, #111111);" if ("explicit" in val_key or "high" in val_key) else ""
    )

    return (
        f'<span class="dp-badge" style="background:{bg}; color:{text_c}; '
        f'border: 1.5px {border_style} {border_c}; {thick_edge} {text_dec}">{label}</span>'
    )


def inject_custom_css() -> None:
    """Inject soft neo-brutalist theme CSS with light and dark mode support."""
    theme = get_current_theme()

    # Soft Neo-Brutalist CSS Token Variables
    if theme == "dark":
        theme_vars = """
        --bg: #121212;
        --card: #1E1E1E;
        --ink: #EEEEEE;
        --muted: #A0A0A0;
        --line: #333333;
        --coral: #F26F55;
        --coral-tint: rgba(242, 111, 85, 0.2);
        --blue: #5B8DEF;
        --yellow: #FFC43D;
        --teal: #52C4C0;
        --radius-card: 18px;
        --radius-tile: 16px;
        --radius-pill: 999px;
        --outline: 1.5px;
        --edge: 4px;

        --dp-bg-app: var(--bg);
        --dp-bg-main: var(--bg);
        --dp-surface-page: var(--bg);
        --dp-surface-card: var(--card);
        --dp-surface-secondary: #282828;
        --dp-sidebar-bg: var(--card);
        --dp-sidebar-surface: #282828;
        --dp-sidebar-text: var(--ink);
        --dp-sidebar-border: var(--line);
        --dp-text-primary: var(--ink);
        --dp-text-secondary: #C0C0C0;
        --dp-text-muted: var(--muted);
        --dp-primary: var(--coral);
        --dp-primary-hover: #FF7F66;
        --dp-primary-light: var(--coral-tint);
        --dp-border: var(--ink);
        --dp-border-strong: var(--ink);
        --dp-card-shadow: none;
        --dp-input-bg: var(--card);
        --dp-input-border: var(--ink);
        --dp-input-text: var(--ink);
        --dp-success: var(--teal);
        --dp-error: var(--coral);
        --dp-warning: var(--yellow);
        --dp-info: var(--blue);
        """
    else:  # light (default)
        theme_vars = """
        --bg: #F7F7F7;
        --card: #FFFFFF;
        --ink: #111111;
        --muted: #8A8A8A;
        --line: #E6E6E6;
        --coral: #F26F55;
        --coral-tint: #FDDCD6;
        --blue: #5B8DEF;
        --yellow: #FFC43D;
        --teal: #52C4C0;
        --radius-card: 18px;
        --radius-tile: 16px;
        --radius-pill: 999px;
        --outline: 1.5px;
        --edge: 4px;

        --dp-bg-app: var(--bg);
        --dp-bg-main: var(--bg);
        --dp-surface-page: var(--bg);
        --dp-surface-card: var(--card);
        --dp-surface-secondary: #F0F0F0;
        --dp-sidebar-bg: var(--card);
        --dp-sidebar-surface: #F9F9F9;
        --dp-sidebar-text: var(--ink);
        --dp-sidebar-border: var(--line);
        --dp-text-primary: var(--ink);
        --dp-text-secondary: #4A4A4A;
        --dp-text-muted: var(--muted);
        --dp-primary: var(--coral);
        --dp-primary-hover: #E0563C;
        --dp-primary-light: var(--coral-tint);
        --dp-border: var(--ink);
        --dp-border-strong: var(--ink);
        --dp-card-shadow: none;
        --dp-input-bg: var(--card);
        --dp-input-border: var(--ink);
        --dp-input-text: var(--ink);
        --dp-success: var(--teal);
        --dp-error: var(--coral);
        --dp-warning: var(--yellow);
        --dp-info: var(--blue);
        """

    st.markdown(
        f"""
<style>
/* =========================================================================
   DECISIONPRINT SOFT NEO-BRUTALIST DESIGN SYSTEM (v3)
   Thick bottom edges, pastel tiles, coral primary, Poppins type
   ========================================================================= */

@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {{
    {theme_vars}
    --dp-focus-ring: var(--coral);
}}

/* --- Root & App Canvas --- */
.stApp {{
    background-color: var(--dp-bg-app) !important;
    color: var(--dp-text-primary) !important;
    font-family: 'Poppins', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
    letter-spacing: -0.01em;
}}

/* --- Typography --- */
h1, h2, h3, h4, h5, h6 {{
    font-family: 'Poppins', sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: -0.02em !important;
    color: var(--dp-text-primary) !important;
}}

h1 {{ font-size: 2.1rem !important; margin-bottom: 0.25rem !important; font-weight: 800 !important; }}
h2 {{ font-size: 1.6rem !important; }}
h3 {{ font-size: 1.3rem !important; }}
h4 {{ font-size: 1.1rem !important; }}

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

/* --- Soft Neo-Brutalist Container Wrappers --- */
[data-testid="stVerticalBlockBorderWrapper"] {{
    background-color: var(--card) !important;
    border: var(--outline, 1.5px) solid var(--ink, #111111) !important;
    border-bottom: var(--edge, 4px) solid var(--ink, #111111) !important;
    border-radius: var(--radius-card, 18px) !important;
    box-shadow: none !important;
}}

/* --- Soft Neo-Brutalist Action Buttons --- */
.stButton > button {{
    border-radius: 12px !important;
    padding: 0.5rem 1.25rem !important;
    font-weight: 700 !important;
    font-size: 0.9rem !important;
    border: var(--outline, 1.5px) solid var(--ink, #111111) !important;
    border-bottom: var(--edge, 4px) solid var(--ink, #111111) !important;
    box-shadow: none !important;
    transition: transform 0.1s ease, border-bottom-width 0.1s ease !important;
}}

.stButton > button:hover {{
    transform: translateY(-2px) !important;
}}

.stButton > button:active {{
    transform: translateY(2px) !important;
    border-bottom-width: 2px !important;
}}

/* Primary Buttons */
.stButton > button[kind="primary"],
.stButton > button[data-testid="baseButton-primary"] {{
    background: var(--coral, #F26F55) !important;
    color: #FFFFFF !important;
    border-color: var(--ink, #111111) !important;
}}

.stButton > button[kind="primary"]:hover,
.stButton > button[data-testid="baseButton-primary"]:hover {{
    background: #E0563C !important;
    color: #FFFFFF !important;
}}

/* Secondary / Standard Buttons (Chips & Cards) */
.stButton > button[kind="secondary"],
.stButton > button[data-testid="baseButton-secondary"],
.stButton > button:not([kind="primary"]):not([data-testid="baseButton-primary"]) {{
    background: var(--card, #FFFFFF) !important;
    color: var(--ink, #111111) !important;
    border-color: var(--ink, #111111) !important;
}}

.stButton > button[kind="secondary"]:hover,
.stButton > button[data-testid="baseButton-secondary"]:hover,
.stButton > button:not([kind="primary"]):not([data-testid="baseButton-primary"]):hover {{
    background: var(--dp-surface-secondary, #F0F0F0) !important;
    color: var(--ink, #111111) !important;
}}

/* --- Form Controls & Text Inputs (Outline + Thick bottom edge) --- */
[data-baseweb="input"],
[data-baseweb="base-input"],
[data-baseweb="select"],
.stTextInput > div > div,
.stTextArea > div > div {{
    background-color: var(--card) !important;
    border: var(--outline, 1.5px) solid var(--ink, #111111) !important;
    border-bottom: var(--edge, 4px) solid var(--ink, #111111) !important;
    border-radius: 16px !important;
    color: var(--ink) !important;
    box-shadow: none !important;
    transition: transform 0.15s ease, border-color 0.15s ease !important;
}}

[data-baseweb="select"] > div {{
    background-color: var(--card) !important;
    border: none !important;
    color: var(--ink) !important;
}}

[data-baseweb="input"]:focus-within,
[data-baseweb="select"] > div:focus-within,
.stTextInput > div > div:focus-within {{
    border-color: var(--coral, #F26F55) !important;
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
    color: var(--ink) !important;
    -webkit-text-fill-color: var(--ink) !important;
    caret-color: var(--coral, #F26F55) !important;
    font-family: 'Poppins', system-ui, -apple-system, sans-serif !important;
    font-size: 0.92rem !important;
    font-weight: 500 !important;
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
div[data-testid="stSelectbox"] > div > div,
[data-baseweb="select"],
[data-baseweb="select"] > div,
[data-baseweb="select"] [role="combobox"],
[data-baseweb="select"] [data-aria-hidden="true"],
[data-baseweb="select"] input,
[data-baseweb="select"] div,
[data-baseweb="select"] span {{
    background-color: var(--card) !important;
    color: var(--ink) !important;
    -webkit-text-fill-color: var(--ink) !important;
}}

[data-baseweb="select"] * {{
    color: var(--ink) !important;
    -webkit-text-fill-color: var(--ink) !important;
}}

div[data-baseweb="popover"],
div[data-baseweb="popover"] *,
div[data-baseweb="menu"],
div[data-baseweb="menu"] *,
ul[role="listbox"],
ul[role="listbox"] *,
li[role="option"],
li[role="option"] * {{
    background-color: var(--card) !important;
    color: var(--ink) !important;
    -webkit-text-fill-color: var(--ink) !important;
}}

li[role="option"]:hover,
li[role="option"]:hover *,
li[role="option"][aria-selected="true"],
li[role="option"][aria-selected="true"] * {{
    background-color: var(--coral-tint) !important;
    color: var(--coral) !important;
    -webkit-text-fill-color: var(--coral) !important;
}}

/* Header & App Top Bar Background Alignment */
html, body, .stApp, header, [data-testid="stHeader"], .stAppHeader, [data-testid="stTopNav"], [data-testid="stToolbar"] {{
    background-color: var(--bg) !important;
    color: var(--ink) !important;
}}

header[data-testid="stHeader"],
header.stAppHeader,
.stAppHeader,
[data-testid="stHeader"],
div[data-testid="stHeader"] {{
    background-color: var(--bg) !important;
    background: var(--bg) !important;
    color: var(--ink) !important;
    border-bottom: 1.5px solid var(--line) !important;
}}

[data-testid="stDecoration"] {{
    display: none !important;
}}

/* Force text inside top navigation links to inherit ink color */
div[data-testid="stTopNav"] *,
header nav *,
[data-testid="stHeader"] nav *,
[data-testid="stHeader"] a,
[data-testid="stHeader"] span,
[data-testid="stHeader"] p {{
    color: var(--ink) !important;
    -webkit-text-fill-color: var(--ink) !important;
}}

/* Streamlit Top Navigation Bar Container Centering & Button Styling */
div[data-testid="stTopNav"],
header nav,
[data-testid="stHeader"] nav {{
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
    margin: 0 auto !important;
    background-color: var(--bg) !important;
    padding: 4px 12px !important;
}}

div[data-testid="stTopNav"] ul,
header nav ul,
[data-testid="stHeader"] nav ul {{
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
    gap: 6px !important;
    margin: 0 auto !important;
    padding: 0 !important;
    list-style: none !important;
    background-color: var(--bg) !important;
}}

/* Top Navigation Link Buttons */
div[data-testid="stTopNav"] a,
div[data-testid="stTopNav"] button,
header nav a,
header nav button,
[data-testid="stHeader"] a {{
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    padding: 6px 16px !important;
    border-radius: 999px !important;
    font-family: 'Poppins', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    text-decoration: none !important;
    color: var(--ink) !important;
    -webkit-text-fill-color: var(--ink) !important;
    border: 1.5px solid var(--line) !important;
    background-color: var(--card) !important;
    transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
    box-shadow: none !important;
}}

div[data-testid="stTopNav"] a:hover,
header nav a:hover {{
    border-color: var(--coral) !important;
    color: var(--coral) !important;
    -webkit-text-fill-color: var(--coral) !important;
    background-color: var(--dp-surface-secondary) !important;
}}

/* Active Navigation Page Button */
div[data-testid="stTopNav"] a[aria-current="page"],
div[data-testid="stTopNav"] a[data-selected="true"],
header nav a[aria-current="page"] {{
    background-color: var(--coral, #F26F55) !important;
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
    border: 1.5px solid var(--ink, #111111) !important;
    border-bottom: 3.5px solid var(--ink, #111111) !important;
    font-weight: 700 !important;
}}

div[data-testid="stTopNav"] a[aria-current="page"] *,
header nav a[aria-current="page"] * {{
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
}}

/* ST.CHAT_INPUT AT BOTTOM OF PAGE */
[data-testid="stChatInput"],
[data-testid="stChatInput"] > div,
[data-testid="stChatInput"] div[data-baseweb="textarea"],
[data-testid="stChatInput"] [data-baseweb="base-input"] {{
    background-color: var(--card) !important;
    border: 1.5px solid var(--ink) !important;
    border-bottom: 4px solid var(--ink) !important;
    border-radius: 18px !important;
    color: var(--ink) !important;
}}

[data-testid="stChatInput"] textarea {{
    background-color: transparent !important;
    color: var(--ink) !important;
    -webkit-text-fill-color: var(--ink) !important;
    caret-color: var(--coral) !important;
}}

[data-testid="stChatInput"] textarea::placeholder {{
    color: var(--muted) !important;
    -webkit-text-fill-color: var(--muted) !important;
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

/* Respect prefers-reduced-motion */
@media (prefers-reduced-motion: reduce) {{
    *, ::before, ::after {{
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
        scroll-behavior: auto !important;
        transform: none !important;
    }}
}}
</style>
    """,
        unsafe_allow_html=True,
    )


# Alias for compatibility with Master Prompt v3
inject_theme = inject_custom_css
