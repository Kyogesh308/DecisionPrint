"""Design tokens and theme injection — single source of truth for UI styling."""

from __future__ import annotations

import streamlit as st

__all__ = [
    "CAUSAL_COLORS",
    "COMPARISON_COLORS",
    "DRIFT_COLORS",
    "EPISTEMIC_COLORS",
    "STATUS_COLORS",
    "badge_html",
    "inject_custom_css",
]

# Epistemic types (Fact, Observation, Inference, Recommendation)
EPISTEMIC_COLORS = {
    "fact": {
        "bg": "rgba(59, 130, 246, 0.15)",
        "text": "#60A5FA",
        "border": "rgba(96, 165, 250, 0.35)",
        "label": "FACT",
    },
    "observation": {
        "bg": "rgba(20, 184, 166, 0.15)",
        "text": "#5EEAD4",
        "border": "rgba(94, 234, 212, 0.35)",
        "label": "OBSERVATION",
    },
    "inference": {
        "bg": "rgba(245, 158, 11, 0.15)",
        "text": "#FBBF24",
        "border": "rgba(251, 191, 36, 0.35)",
        "label": "INFERENCE",
    },
    "recommendation": {
        "bg": "rgba(168, 85, 247, 0.15)",
        "text": "#C084FC",
        "border": "rgba(192, 132, 252, 0.35)",
        "label": "RECOMMENDATION",
    },
}

# Drift levels
DRIFT_COLORS = {
    "none": {
        "bg": "rgba(34, 197, 94, 0.15)",
        "text": "#4ADE80",
        "border": "rgba(74, 222, 128, 0.4)",
        "label": "NO DRIFT",
    },
    "low": {
        "bg": "rgba(234, 179, 8, 0.15)",
        "text": "#FACC15",
        "border": "rgba(250, 204, 21, 0.4)",
        "label": "LOW DRIFT",
    },
    "medium": {
        "bg": "rgba(249, 115, 22, 0.15)",
        "text": "#FB923C",
        "border": "rgba(251, 146, 60, 0.4)",
        "label": "MEDIUM DRIFT",
    },
    "high": {
        "bg": "rgba(239, 68, 68, 0.18)",
        "text": "#F87171",
        "border": "rgba(248, 113, 113, 0.5)",
        "label": "HIGH DRIFT",
    },
}

# Comparison badges
COMPARISON_COLORS = {
    "same": {
        "bg": "rgba(148, 163, 184, 0.12)",
        "text": "#94A3B8",
        "border": "rgba(148, 163, 184, 0.25)",
        "label": "UNCHANGED",
    },
    "changed": {
        "bg": "rgba(239, 68, 68, 0.15)",
        "text": "#F87171",
        "border": "rgba(248, 113, 113, 0.35)",
        "label": "CHANGED",
    },
    "newly_present": {
        "bg": "rgba(249, 115, 22, 0.15)",
        "text": "#FB923C",
        "border": "rgba(251, 146, 60, 0.35)",
        "label": "NEW",
    },
    "unknown": {
        "bg": "rgba(100, 116, 139, 0.12)",
        "text": "#64748B",
        "border": "rgba(100, 116, 139, 0.2)",
        "label": "UNKNOWN",
    },
    "incomparable": {
        "bg": "rgba(100, 116, 139, 0.12)",
        "text": "#64748B",
        "border": "rgba(100, 116, 139, 0.2)",
        "label": "N/A",
    },
}

# Causal link labels
CAUSAL_COLORS = {
    "explicit_causal_link": {
        "bg": "rgba(99, 102, 241, 0.22)",
        "text": "#818CF8",
        "border": "#6366F1",
        "label": "EXPLICIT CAUSAL LINK",
    },
    "strong_evidence": {
        "bg": "rgba(20, 184, 166, 0.18)",
        "text": "#5EEAD4",
        "border": "rgba(94, 234, 212, 0.4)",
        "label": "STRONG EVIDENCE",
    },
    "possible_causal_link": {
        "bg": "rgba(245, 158, 11, 0.18)",
        "text": "#FBBF24",
        "border": "rgba(251, 191, 36, 0.4)",
        "label": "POSSIBLE LINK",
    },
    "fact": {
        "bg": "rgba(59, 130, 246, 0.18)",
        "text": "#60A5FA",
        "border": "rgba(96, 165, 250, 0.4)",
        "label": "DOCUMENTED FACT",
    },
    "none": {"bg": "transparent", "text": "", "border": "transparent", "label": ""},
}

# Decision status
STATUS_COLORS = {
    "active": {
        "bg": "rgba(34, 197, 94, 0.15)",
        "text": "#4ADE80",
        "border": "rgba(74, 222, 128, 0.35)",
        "label": "ACTIVE",
    },
    "superseded": {
        "bg": "rgba(249, 115, 22, 0.15)",
        "text": "#FB923C",
        "border": "rgba(251, 146, 60, 0.35)",
        "label": "SUPERSEDED",
    },
    "reconsidered": {
        "bg": "rgba(59, 130, 246, 0.15)",
        "text": "#60A5FA",
        "border": "rgba(96, 165, 250, 0.35)",
        "label": "RECONSIDERED",
    },
}


def badge_html(category: str, value: str) -> str:
    """Return sleek styled HTML badge with border glow and monospace typography."""
    lookup = {
        "epistemic": EPISTEMIC_COLORS,
        "drift": DRIFT_COLORS,
        "comparison": COMPARISON_COLORS,
        "causal": CAUSAL_COLORS,
        "status": STATUS_COLORS,
    }
    c_map = lookup.get(category, {})
    val_key = value.lower() if value else ""
    colors = c_map.get(
        val_key,
        {
            "bg": "rgba(100, 116, 139, 0.2)",
            "text": "#94A3B8",
            "border": "rgba(148, 163, 184, 0.3)",
            "label": value.upper(),
        },
    )

    label = colors.get("label", "")
    if not label:
        return ""

    glow = f"box-shadow: 0 0 12px {colors['border']}30;" if "explicit" in val_key or "high" in val_key else ""
    return (
        f'<span class="dp-badge" style="background:{colors["bg"]}; color:{colors["text"]}; '
        f'border: 1px solid {colors["border"]}; {glow}">{label}</span>'
    )


def inject_custom_css() -> None:
    """Inject UI/UX Pro Max Modern Dark design system CSS into Streamlit."""
    st.markdown(
        """
<style>
/* =========================================================================
   UI/UX PRO MAX — CINEMATIC MODERN DARK (DECISIONPRINT DESIGN SYSTEM)
   Palette: Deep Navy Canvas (#0B0F19), Slate Glass (#151D2F), Indigo/Cyan (#6366F1 / #38BDF8)
   ========================================================================= */

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

/* --- Root & App Canvas --- */
.stApp {
    background: radial-gradient(circle at 10% 10%, rgba(99, 102, 241, 0.07) 0%, transparent 45%),
                radial-gradient(circle at 90% 90%, rgba(56, 189, 248, 0.05) 0%, transparent 50%),
                #0B0F19 !important;
    color: #F8FAFC !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
    letter-spacing: -0.01em;
}

/* --- Typography --- */
h1, h2, h3, h4, h5, h6 {
    font-family: 'Inter', sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: -0.025em !important;
    color: #F8FAFC !important;
}

h1 { font-size: 2.25rem !important; }
h2 { font-size: 1.75rem !important; }
h3 { font-size: 1.35rem !important; }
h4 { font-size: 1.1rem !important; }

p, span, label, div {
    color: #E2E8F0;
}

/* Custom Scrollbar */
::-webkit-scrollbar {
    width: 7px;
    height: 7px;
}
::-webkit-scrollbar-track {
    background: #0B0F19;
}
::-webkit-scrollbar-thumb {
    background: #1E293B;
    border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
    background: #6366F1;
}

/* --- Sidebar Glassmorphism --- */
[data-testid="stSidebar"] {
    background: rgba(11, 15, 25, 0.9) !important;
    backdrop-filter: blur(20px) !important;
    -webkit-backdrop-filter: blur(20px) !important;
    border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
}

.dp-sidebar-logo {
    font-size: 1.85rem !important;
    font-weight: 800 !important;
    background: linear-gradient(135deg, #818CF8 0%, #38BDF8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0 !important;
    letter-spacing: -0.03em;
}

.dp-sidebar-sub {
    font-size: 0.78rem !important;
    color: #94A3B8 !important;
    margin-top: 0 !important;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

.dp-backend-badge {
    margin-top: 1.5rem;
    padding: 0.45rem 0.8rem;
    border: 1px solid;
    border-radius: 9999px;
    text-align: center;
    font-size: 0.72rem;
    font-family: 'JetBrains Mono', monospace;
    font-weight: 700;
    letter-spacing: 0.08em;
    background: rgba(30, 41, 59, 0.6);
    box-shadow: 0 0 15px rgba(99, 102, 241, 0.15);
}

.dp-version {
    margin-top: 0.75rem;
    text-align: center;
    font-size: 0.72rem;
    color: #64748B;
    font-family: 'JetBrains Mono', monospace;
}

/* --- Hero Banner --- */
.dp-hero {
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(56, 189, 248, 0.08) 50%, rgba(168, 85, 247, 0.12) 100%) !important;
    border: 1px solid rgba(99, 102, 241, 0.35) !important;
    border-radius: 18px !important;
    padding: 2.5rem 2rem !important;
    text-align: center !important;
    margin-bottom: 2rem !important;
    box-shadow: 0 12px 35px -10px rgba(99, 102, 241, 0.25), inset 0 1px 0 rgba(255, 255, 255, 0.15) !important;
    position: relative !important;
    overflow: hidden !important;
}

.dp-hero h1 {
    font-size: 3rem !important;
    background: linear-gradient(135deg, #FFFFFF 20%, #A5B4FC 60%, #38BDF8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.6rem !important;
}

.dp-hero-sub {
    font-size: 1.15rem !important;
    color: #CBD5E1 !important;
    max-width: 650px;
    margin: 0 auto;
    font-weight: 400;
    line-height: 1.6;
}

/* --- Glassmorphic Cards --- */
.dp-card {
    background: rgba(21, 29, 47, 0.75) !important;
    backdrop-filter: blur(16px) !important;
    -webkit-backdrop-filter: blur(16px) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 14px !important;
    padding: 1.4rem 1.6rem !important;
    margin-bottom: 1.25rem !important;
    box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.5), inset 0 1px 0 0 rgba(255, 255, 255, 0.06) !important;
    transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
}

.dp-card:hover {
    border-color: rgba(99, 102, 241, 0.4) !important;
    box-shadow: 0 8px 30px -4px rgba(0, 0, 0, 0.6), 0 0 20px rgba(99, 102, 241, 0.2) !important;
    transform: translateY(-2px) !important;
}

/* --- Badges & Micro-tags --- */
.dp-badge {
    display: inline-flex !important;
    align-items: center !important;
    padding: 3px 10px !important;
    border-radius: 9999px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.03em !important;
    text-transform: uppercase !important;
    line-height: 1.2 !important;
}

.dp-badge-review {
    border: 1px solid #F59E0B !important;
    background: rgba(245, 158, 11, 0.18) !important;
    color: #FBBF24 !important;
    box-shadow: 0 0 12px rgba(245, 158, 11, 0.35) !important;
    animation: dp-pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite !important;
}

@keyframes dp-pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.8; transform: scale(1.04); }
}

/* --- Code & Monospace Elements --- */
code {
    font-family: 'JetBrains Mono', monospace !important;
    background: rgba(99, 102, 241, 0.12) !important;
    color: #93C5FD !important;
    padding: 0.15rem 0.45rem !important;
    border-radius: 6px !important;
    border: 1px solid rgba(99, 102, 241, 0.25) !important;
    font-size: 0.88em !important;
}

/* --- Streamlit Native Overrides --- */
/* Buttons */
.stButton > button {
    background: linear-gradient(180deg, #1E293B 0%, #151D2F 100%) !important;
    color: #F8FAFC !important;
    border: 1px solid rgba(255, 255, 255, 0.12) !important;
    border-radius: 10px !important;
    padding: 0.5rem 1.25rem !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.35) !important;
}

.stButton > button:hover {
    border-color: #6366F1 !important;
    box-shadow: 0 0 15px rgba(99, 102, 241, 0.4) !important;
    transform: translateY(-1px) !important;
    color: #FFFFFF !important;
}

.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #6366F1 0%, #4F46E5 100%) !important;
    border: 1px solid #818CF8 !important;
    box-shadow: 0 4px 18px rgba(99, 102, 241, 0.45) !important;
}

.stButton > button[kind="primary"]:hover {
    box-shadow: 0 6px 24px rgba(99, 102, 241, 0.65) !important;
    transform: translateY(-2px) !important;
}

/* Inputs & Form Fields */
.stTextInput > div > div > input,
.stSelectbox > div > div,
.stTextArea textarea {
    background-color: #0F172A !important;
    border: 1px solid #334155 !important;
    border-radius: 10px !important;
    color: #F8FAFC !important;
    font-size: 0.95rem !important;
    transition: all 0.2s ease !important;
}

.stTextInput > div > div > input:focus,
.stTextArea textarea:focus {
    border-color: #6366F1 !important;
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.25) !important;
}

/* Metric Display Cards */
[data-testid="stMetricValue"] {
    font-family: 'Inter', sans-serif !important;
    font-weight: 800 !important;
    font-size: 2.1rem !important;
    color: #F8FAFC !important;
    background: linear-gradient(180deg, #FFFFFF 40%, #94A3B8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

[data-testid="stMetricLabel"] {
    color: #94A3B8 !important;
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
}

/* Progress Bars */
[data-testid="stProgress"] > div > div > div > div {
    background: linear-gradient(90deg, #6366F1 0%, #38BDF8 100%) !important;
    border-radius: 9999px !important;
}

/* Tabs */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    gap: 8px;
    background: transparent;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

[data-testid="stTabs"] [data-baseweb="tab"] {
    background: transparent !important;
    border-radius: 8px 8px 0 0 !important;
    color: #94A3B8 !important;
    font-weight: 600 !important;
    padding: 0.6rem 1.2rem !important;
    border: none !important;
}

[data-testid="stTabs"] [aria-selected="true"] {
    color: #818CF8 !important;
    border-bottom: 2px solid #6366F1 !important;
}

/* Modals & Dialogs */
[data-testid="stDialog"] div[role="dialog"] {
    background: #0F172A !important;
    border: 1px solid rgba(99, 102, 241, 0.4) !important;
    border-radius: 16px !important;
    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.8), 0 0 30px rgba(99, 102, 241, 0.2) !important;
}

/* Timeline Components */
.dp-timeline-item {
    position: relative;
    padding-left: 2.2rem;
    padding-bottom: 1.6rem;
    border-left: 2px solid #27354A;
}

.dp-timeline-item:last-child {
    border-left: 2px solid transparent;
}

.dp-timeline-dot {
    position: absolute;
    left: -7px;
    top: 4px;
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background: #6366F1;
    box-shadow: 0 0 12px #6366F1;
}

.dp-timeline-date {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem;
    color: #94A3B8;
    margin-bottom: 0.3rem;
}

.dp-chain-arrow {
    font-size: 1.6rem;
    color: #818CF8;
    text-align: center;
    margin: 0.6rem 0;
    filter: drop-shadow(0 0 8px rgba(99, 102, 241, 0.6));
}
</style>
    """,
        unsafe_allow_html=True,
    )
