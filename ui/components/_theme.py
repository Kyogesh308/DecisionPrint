"""Theme tokens and CSS injection for light and dark modes."""

from __future__ import annotations

import re
from string import Template
from typing import Literal

import streamlit as st

ThemeMode = Literal["light", "dark"]

_SHARED = {
    "coral": "#F26F55",
    "blue": "#5B8DEF",
    "yellow": "#FFC43D",
    "teal": "#52C4C0",
    "ink": "#111111",  # text on pastel tiles, in BOTH modes
    "on_coral": "#111111",  # text on coral, in BOTH modes (contrast ~6.5:1)
}

TOKENS: dict[ThemeMode, dict[str, str]] = {
    "light": {
        **_SHARED,
        "bg": "#F7F7F7",
        "surface": "#FFFFFF",
        "surface2": "#F0F0F0",
        "text": "#111111",
        "muted": "#6B6B6B",
        "line": "#E0E0E0",
        "edge": "#111111",
    },
    "dark": {
        **_SHARED,
        "bg": "#121212",
        "surface": "#1C1C1E",
        "surface2": "#26262A",
        "text": "#F5F5F5",
        "muted": "#A3A3A8",
        "line": "#333338",
        "edge": "#EDEDED",
    },
}

# Color maps preserved for badge_html lookup
EPISTEMIC_COLORS = {
    "fact": {"label": "FACT", "bg": "var(--blue)", "text": "var(--ink)", "border": "var(--edge)"},
    "observation": {"label": "OBSERVATION", "bg": "var(--teal)", "text": "var(--ink)", "border": "var(--edge)"},
    "inference": {"label": "INFERENCE", "bg": "var(--yellow)", "text": "var(--ink)", "border": "var(--edge)"},
    "recommendation": {
        "label": "RECOMMENDATION",
        "bg": "var(--text)",
        "text": "var(--bg)",
        "border": "var(--edge)",
    },
}

DRIFT_COLORS = {
    "none": {"label": "NO DRIFT", "bg": "var(--teal)", "text": "var(--ink)", "border": "var(--edge)"},
    "low": {"label": "LOW DRIFT", "bg": "var(--yellow)", "text": "var(--ink)", "border": "var(--edge)"},
    "medium": {"label": "MEDIUM DRIFT", "bg": "var(--coral)", "text": "var(--on_coral)", "border": "var(--edge)"},
    "high": {"label": "HIGH DRIFT", "bg": "var(--coral)", "text": "var(--on_coral)", "border": "var(--edge)"},
}

COMPARISON_COLORS = {
    "same": {"label": "UNCHANGED", "bg": "var(--surface2)", "text": "var(--text)", "border": "var(--line)"},
    "changed": {"label": "CHANGED", "bg": "var(--coral)", "text": "var(--on_coral)", "border": "var(--edge)"},
    "newly_present": {"label": "NEW", "bg": "var(--yellow)", "text": "var(--ink)", "border": "var(--edge)"},
    "unknown": {
        "label": "UNKNOWN",
        "bg": "var(--surface2)",
        "text": "var(--muted)",
        "border": "var(--line)",
        "border_style": "dashed",
    },
    "incomparable": {
        "label": "INCOMPARABLE",
        "bg": "var(--surface2)",
        "text": "var(--muted)",
        "border": "var(--line)",
        "text_decoration": "line-through",
    },
}

CAUSAL_COLORS = {
    "explicit_causal_link": {
        "label": "EXPLICIT CAUSAL LINK",
        "bg": "var(--blue)",
        "text": "var(--ink)",
        "border": "var(--edge)",
    },
    "strong_evidence": {
        "label": "STRONG EVIDENCE",
        "bg": "var(--teal)",
        "text": "var(--ink)",
        "border": "var(--edge)",
    },
    "possible_causal_link": {
        "label": "POSSIBLE LINK",
        "bg": "var(--yellow)",
        "text": "var(--ink)",
        "border": "var(--edge)",
    },
    "fact": {"label": "DOCUMENTED FACT", "bg": "var(--blue)", "text": "var(--ink)", "border": "var(--edge)"},
    "none": {"label": "", "bg": "transparent", "text": "", "border": "transparent"},
}

STATUS_COLORS = {
    "active": {"label": "ACTIVE", "bg": "var(--teal)", "text": "var(--ink)", "border": "var(--edge)"},
    "implemented": {
        "label": "IMPLEMENTED",
        "bg": "var(--teal)",
        "text": "var(--ink)",
        "border": "var(--edge)",
    },
    "planned": {"label": "PLANNED", "bg": "var(--blue)", "text": "var(--ink)", "border": "var(--edge)"},
    "reconsider": {
        "label": "RECONSIDER",
        "bg": "var(--yellow)",
        "text": "var(--ink)",
        "border": "var(--edge)",
    },
    "rejected": {"label": "REJECTED", "bg": "var(--coral)", "text": "var(--on_coral)", "border": "var(--edge)"},
    "on_hold": {"label": "ON HOLD", "bg": "var(--yellow)", "text": "var(--ink)", "border": "var(--edge)"},
    "completed": {"label": "COMPLETED", "bg": "var(--teal)", "text": "var(--ink)", "border": "var(--edge)"},
    "revisited": {"label": "REVISITED", "bg": "var(--blue)", "text": "var(--ink)", "border": "var(--edge)"},
    "superseded": {
        "label": "SUPERSEDED",
        "bg": "var(--yellow)",
        "text": "var(--ink)",
        "border": "var(--edge)",
    },
    "reconsidered": {
        "label": "RECONSIDERED",
        "bg": "var(--blue)",
        "text": "var(--ink)",
        "border": "var(--edge)",
    },
}

_CSS = Template("""
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap');
:root{color-scheme:$mode;--bg:$bg;--surface:$surface;--surface2:$surface2;--text:$text;
--muted:$muted;--line:$line;--edge:$edge;--coral:$coral;--blue:$blue;--yellow:$yellow;
--teal:$teal;--ink:$ink;--on-coral:$on_coral;--dp-bg-app:$bg;--dp-bg-main:$bg;
--dp-surface-page:$bg;--dp-surface-card:$surface;--dp-surface-secondary:$surface2;
--dp-sidebar-bg:$surface;--dp-sidebar-surface:$surface2;--dp-sidebar-text:$text;
--dp-sidebar-border:$line;--dp-text-primary:$text;--dp-text-secondary:$muted;
--dp-text-muted:$muted;--dp-primary:$coral;--dp-primary-hover:$coral;
--dp-primary-light:$surface2;--dp-border:$edge;--dp-border-strong:$edge;
--dp-card-shadow:none;--dp-input-bg:$surface;--dp-input-border:$edge;
--dp-input-text:$text;--dp-success:$teal;--dp-error:$coral;--dp-warning:$yellow;
--dp-info:$blue;--radius-card:18px;--radius-tile:16px;--radius-pill:999px;
--outline:1.5px;--edge:4px;}
html,body,.stApp,[data-testid="stAppViewContainer"],[data-testid="stMain"]{
font-family:Poppins,system-ui,"Segoe UI",Roboto,Arial,sans-serif;background:$bg!important;color:$text!important;}

/* ---- text: explicit colour everywhere, never inherited ---- */
.stApp h1,.stApp h2,.stApp h3,.stApp h4,.stApp h5,.stApp h6,.stApp p,.stApp li,
.stApp label,.stApp legend,.stApp [data-testid="stMarkdownContainer"],
.stApp [data-testid="stWidgetLabel"] *{color:$text!important;}
.stApp [data-testid="stCaptionContainer"],.stApp small{color:$muted!important;}

/* ---- top navigation / header ---- */
[data-testid="stHeader"],.stAppHeader,header,div[data-testid="stHeader"]{background:$bg!important;
border-bottom:1.5px solid $line!important;color:$text!important;}
[data-testid="stHeader"] *{color:$text!important;}
[data-testid="stDecoration"]{display:none!important;}
[data-testid="stTopNav"],header nav{display:flex!important;justify-content:center!important;
align-items:center!important;margin:0 auto!important;background:$bg!important;}
[data-testid="stTopNav"] ul,header nav ul{display:flex!important;justify-content:center!important;
align-items:center!important;gap:6px!important;margin:0 auto!important;padding:4px 0!important;
list-style:none!important;background:$bg!important;}
[data-testid="stTopNav"] a,[data-testid="stTopNav"] button,header nav a,header nav button{
display:inline-flex!important;align-items:center!important;justify-content:center!important;
padding:6px 16px!important;border-radius:999px!important;font-family:'Poppins',sans-serif!important;
font-weight:600!important;font-size:0.88rem!important;text-decoration:none!important;
color:$text!important;-webkit-text-fill-color:$text!important;border:1.5px solid $line!important;
background:$surface!important;transition:all 0.2s ease!important;}
[data-testid="stTopNav"] a:hover,header nav a:hover{border-color:$coral!important;
color:$coral!important;-webkit-text-fill-color:$coral!important;background:$surface2!important;}
[data-testid="stTopNav"] a[aria-current="page"],[data-testid="stTopNav"] a[data-selected="true"],
header nav a[aria-current="page"]{background:$coral!important;color:$on_coral!important;
-webkit-text-fill-color:$on_coral!important;border:1.5px solid $edge!important;
border-bottom:3.5px solid $edge!important;font-weight:700!important;}
[data-testid="stTopNav"] a[aria-current="page"] *,header nav a[aria-current="page"] *{
color:$on_coral!important;-webkit-text-fill-color:$on_coral!important;}

/* ---- inputs, selects, text areas ---- */
.stApp [data-baseweb="select"]>div,.stApp [data-baseweb="input"],
.stApp [data-baseweb="base-input"],.stApp [data-baseweb="textarea"],
.stApp input,.stApp textarea{background:$surface!important;color:$text!important;
-webkit-text-fill-color:$text!important;border:1.5px solid $edge!important;
border-bottom:4px solid $edge!important;border-radius:16px!important;}
.stApp [data-baseweb="select"] *{color:$text!important;-webkit-text-fill-color:$text!important;}
.stApp [data-baseweb="select"] svg{fill:$text!important;color:$text!important;}
.stApp input::placeholder,.stApp textarea::placeholder{color:$muted!important;
-webkit-text-fill-color:$muted!important;opacity:1!important;}

/* ---- portals: rendered OUTSIDE .stApp, so NO .stApp prefix ---- */
[data-baseweb="popover"],[data-baseweb="popover"] ul,[data-baseweb="menu"]{
background:$surface!important;color:$text!important;}
[data-baseweb="popover"] li,[data-baseweb="popover"] li *{background:$surface!important;
color:$text!important;-webkit-text-fill-color:$text!important;}
[data-baseweb="popover"] li:hover,[data-baseweb="popover"] li:hover *,
[data-baseweb="popover"] li[aria-selected="true"]{background:$surface2!important;
color:$coral!important;-webkit-text-fill-color:$coral!important;}
[data-baseweb="tooltip"],[data-baseweb="tooltip"] div{background:$surface!important;
color:$text!important;-webkit-text-fill-color:$text!important;border:1.5px solid $edge!important;
border-radius:10px!important;}
div[role="dialog"],div[role="dialog"] *{color:$text!important;-webkit-text-fill-color:$text!important;}
div[role="dialog"]{background:$surface!important;border:1.5px solid $edge!important;
border-bottom:4px solid $edge!important;border-radius:18px!important;}

/* ---- chat input + bottom bar ---- */
[data-testid="stBottom"],[data-testid="stBottom"]>div,
[data-testid="stBottomBlockContainer"]{background:$bg!important;}
[data-testid="stChatInput"]{background:$surface!important;border:1.5px solid $edge!important;
border-bottom:4px solid $edge!important;border-radius:16px!important;}
[data-testid="stChatInput"] textarea{background:transparent!important;color:$text!important;
-webkit-text-fill-color:$text!important;}
[data-testid="stChatInput"] button{background:$coral!important;color:$on_coral!important;
border-radius:12px!important;}
[data-testid="stChatInput"] button svg{fill:$on_coral!important;}
[data-testid="stChatMessage"]{background:transparent!important;}

/* ---- buttons ---- */
.stApp [data-testid="stBaseButton-secondary"],.stApp .stButton>button:not([kind="primary"]){
background:$surface!important;color:$text!important;border:1.5px solid $edge!important;
border-bottom:4px solid $edge!important;border-radius:14px!important;}
.stApp [data-testid="stBaseButton-secondary"] *,.stApp .stButton>button:not([kind="primary"]) *{
color:$text!important;}
.stApp [data-testid="stBaseButton-primary"],.stApp .stButton>button[kind="primary"]{
background:$coral!important;color:$on_coral!important;border:1.5px solid $edge!important;
border-bottom:4px solid $edge!important;border-radius:14px!important;font-weight:600!important;}
.stApp [data-testid="stBaseButton-primary"] *,.stApp .stButton>button[kind="primary"] *{
color:$on_coral!important;}
.stApp .stButton>button:hover{transform:translateY(-1px)!important;}
.stApp .stButton>button:active{transform:translateY(2px)!important;border-bottom-width:2px!important;}

/* ---- tabs, expanders ---- */
.stApp [data-baseweb="tab"]{color:$muted!important;}
.stApp [data-baseweb="tab"][aria-selected="true"]{color:$text!important;font-weight:600!important;}
.stApp [data-testid="stExpander"] details{background:$surface!important;border:1.5px solid $edge!important;
border-bottom:4px solid $edge!important;border-radius:18px!important;}

/* ---- DecisionPrint components ---- */
.stApp .dp-card{background:$surface!important;color:$text!important;border:1.5px solid $edge!important;
border-bottom:4px solid $edge!important;border-radius:18px!important;padding:16px 20px!important;}
.stApp .dp-tile{border-radius:16px!important;padding:16px!important;color:$ink!important;}
.stApp .dp-tile,.stApp .dp-tile *{color:$ink!important;}
.stApp .dp-tile.blue{background:$blue!important;}.stApp .dp-tile.yellow{background:$yellow!important;}
.stApp .dp-tile.teal{background:$teal!important;}.stApp .dp-tile.coral{background:$coral!important;}
.stApp .dp-pill{display:inline-block!important;border-radius:999px!important;padding:2px 10px!important;
font-size:12px!important;font-weight:600!important;border:1.5px solid $edge!important;color:$ink!important;}
.stApp .dp-pill.fact{background:$blue!important;}.stApp .dp-pill.observation{background:$teal!important;}
.stApp .dp-pill.inference{background:$yellow!important;}
.stApp .dp-pill.recommendation{background:$text!important;color:$bg!important;}
.stApp .dp-pill.changed,.stApp .dp-pill.high{background:$coral!important;}
.stApp .dp-pill.same{background:$surface2!important;color:$text!important;}
@media (prefers-reduced-motion:reduce){*{transition:none!important;animation:none!important;}}
""")


def resolve_mode() -> ThemeMode:
    """Return the active theme mode from session state toggle else Streamlit native theme."""
    mode = st.session_state.get("theme_mode") or st.session_state.get("theme")
    if mode in ("light", "dark"):
        return mode
    try:
        native = getattr(st.context.theme, "type", None)
    except Exception:  # noqa: BLE001
        native = None
    return "dark" if native == "dark" else "light"


def get_current_theme() -> str:
    """Return the active user theme: 'light', 'dark', or 'system'."""
    return resolve_mode()


def set_current_theme(theme_name: str) -> None:
    """Set the active theme preference across all synced keys."""
    if theme_name in ("light", "dark", "system"):
        st.session_state["theme"] = theme_name
        st.session_state["theme_mode"] = theme_name
        st.session_state["app_theme_radio_sidebar"] = theme_name
        if "settings_theme_radio" in st.session_state:
            st.session_state["settings_theme_radio"] = theme_name


def badge_html(category: str, value: str) -> str:
    """Return soft neo-brutalist styled HTML badge."""
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
            "label": value.upper() if value else "",
            "bg": "var(--surface2)",
            "text": "var(--text)",
            "border": "var(--edge)",
        },
    )

    label = colors.get("label", "")
    if not label:
        return ""

    bg = colors.get("bg", "var(--surface2)")
    text_c = colors.get("text", "var(--text)")
    border_c = colors.get("border", "var(--edge)")
    border_style = colors.get("border_style", "solid")
    text_dec = f"text-decoration: {colors['text_decoration']};" if "text_decoration" in colors else ""

    return (
        f'<span class="dp-badge" style="background:{bg}; color:{text_c}; '
        f'border: 1.5px {border_style} {border_c}; {text_dec}">{label}</span>'
    )


def inject_theme(mode: ThemeMode | None = None) -> ThemeMode:
    """Inject minified theme CSS for the given mode and return the mode used."""
    active = mode or resolve_mode()
    css = re.sub(r"/\*.*?\*/", "", _CSS.substitute(TOKENS[active], mode=active), flags=re.DOTALL)
    minified_css = re.sub(r"\s+", " ", css).strip()
    st.markdown(f"<style>{minified_css}</style>", unsafe_allow_html=True)
    return active


# Alias for backward compatibility
inject_custom_css = inject_theme

__all__ = [
    "CAUSAL_COLORS",
    "COMPARISON_COLORS",
    "DRIFT_COLORS",
    "EPISTEMIC_COLORS",
    "STATUS_COLORS",
    "TOKENS",
    "ThemeMode",
    "badge_html",
    "get_current_theme",
    "inject_custom_css",
    "inject_theme",
    "resolve_mode",
    "set_current_theme",
]
