"""Design tokens and theme injection — single source of truth for enterprise SaaS UI styling."""

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

# Decision & Lifecycle status
STATUS_COLORS = {
    "active": {
        "bg": "rgba(34, 197, 94, 0.15)",
        "text": "#4ADE80",
        "border": "rgba(74, 222, 128, 0.35)",
        "label": "ACTIVE",
    },
    "implemented": {
        "bg": "rgba(34, 197, 94, 0.15)",
        "text": "#4ADE80",
        "border": "rgba(74, 222, 128, 0.35)",
        "label": "IMPLEMENTED",
    },
    "planned": {
        "bg": "rgba(56, 189, 248, 0.15)",
        "text": "#38BDF8",
        "border": "rgba(56, 189, 248, 0.35)",
        "label": "PLANNED",
    },
    "reconsider": {
        "bg": "rgba(245, 158, 11, 0.15)",
        "text": "#FBBF24",
        "border": "rgba(251, 191, 36, 0.35)",
        "label": "RECONSIDER",
    },
    "rejected": {
        "bg": "rgba(239, 68, 68, 0.15)",
        "text": "#F87171",
        "border": "rgba(248, 113, 113, 0.35)",
        "label": "REJECTED",
    },
    "on_hold": {
        "bg": "rgba(245, 158, 11, 0.15)",
        "text": "#FBBF24",
        "border": "rgba(251, 191, 36, 0.35)",
        "label": "ON HOLD",
    },
    "completed": {
        "bg": "rgba(20, 184, 166, 0.15)",
        "text": "#5EEAD4",
        "border": "rgba(94, 234, 212, 0.35)",
        "label": "COMPLETED",
    },
    "revisited": {
        "bg": "rgba(99, 102, 241, 0.15)",
        "text": "#818CF8",
        "border": "rgba(129, 140, 248, 0.35)",
        "label": "REVISITED",
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
    val_key = value.lower().replace(" ", "_") if value else ""
    colors = c_map.get(
        val_key,
        {
            "bg": "rgba(100, 116, 139, 0.2)",
            "text": "#94A3B8",
            "border": "rgba(148, 163, 184, 0.3)",
            "label": value.upper() if value else "",
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
   DECISIONPRINT ENTERPRISE SAAS DESIGN SYSTEM (MODERN DARK PRO)
   Palette: Deep Midnight Navy Canvas (#080D1A / #0B0F19), Elevated Slate (#111827 / #151D2F)
   Accents: Indigo (#6366F1 / #818CF8), Cyan (#38BDF8), Emerald (#10B981)
   ========================================================================= */

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

/* --- Root & App Canvas --- */
.stApp {
    background: radial-gradient(circle at 10% 8%, rgba(99, 102, 241, 0.05) 0%, transparent 40%),
                radial-gradient(circle at 90% 92%, rgba(56, 189, 248, 0.04) 0%, transparent 45%),
                #080D1A !important;
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

h1 { font-size: 2.1rem !important; }
h2 { font-size: 1.65rem !important; }
h3 { font-size: 1.25rem !important; }
h4 { font-size: 1.05rem !important; }

p, span, label, div {
    color: #E2E8F0;
}

/* Custom Scrollbar */
::-webkit-scrollbar {
    width: 6px;
    height: 6px;
}
::-webkit-scrollbar-track {
    background: #080D1A;
}
::-webkit-scrollbar-thumb {
    background: #1E293B;
    border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
    background: #6366F1;
}

/* --- Sidebar Shell --- */
[data-testid="stSidebar"] {
    background: rgba(11, 15, 25, 0.95) !important;
    backdrop-filter: blur(20px) !important;
    -webkit-backdrop-filter: blur(20px) !important;
    border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
}

.dp-sidebar-header {
    padding: 0.5rem 0 1rem 0;
}

.dp-sidebar-logo-group {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.dp-sidebar-brand-name {
    font-size: 1.35rem;
    font-weight: 800;
    color: #FFFFFF;
    letter-spacing: -0.03em;
}

.dp-sidebar-brand-sub {
    font-size: 0.72rem;
    color: #818CF8;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-weight: 600;
}

.dp-sidebar-divider {
    height: 1px;
    background: rgba(255, 255, 255, 0.08);
    margin: 1rem 0;
}

.dp-sidebar-status-card {
    background: rgba(17, 24, 39, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 10px;
    padding: 0.75rem 0.9rem;
    margin-top: 1rem;
}

.dp-sidebar-status-pill {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.75rem;
    color: #CBD5E1;
    font-family: 'JetBrains Mono', monospace;
}

.dp-status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #10B981;
    box-shadow: 0 0 8px #10B981;
    display: inline-block;
}

.dp-sidebar-status-detail {
    display: flex;
    align-items: center;
    gap: 0.4rem;
    font-size: 0.72rem;
    color: #94A3B8;
    margin-top: 0.4rem;
}

.dp-sidebar-spacer {
    height: 2rem;
}

.dp-sidebar-user-card {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    background: rgba(21, 29, 47, 0.7);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 10px;
    padding: 0.7rem 0.85rem;
    margin-top: 1rem;
}

.dp-user-avatar-lg {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    background: linear-gradient(135deg, #6366F1, #8B5CF6);
    color: #FFFFFF;
    font-weight: 700;
    font-size: 0.85rem;
    display: flex;
    align-items: center;
    justify-content: center;
    border: 1.5px solid rgba(255, 255, 255, 0.2);
}

.dp-user-info {
    display: flex;
    flex-direction: column;
}

.dp-user-name {
    font-size: 0.85rem;
    font-weight: 600;
    color: #F8FAFC;
}

.dp-user-role {
    font-size: 0.72rem;
    color: #94A3B8;
}

.dp-sidebar-version {
    font-size: 0.7rem;
    color: #475569;
    font-family: 'JetBrains Mono', monospace;
    text-align: center;
    margin-top: 0.75rem;
}

/* --- Top Bar Component --- */
.dp-topbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: rgba(15, 23, 42, 0.85);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 0.65rem 1.25rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.4);
}

.dp-topbar-left {
    display: flex;
    align-items: center;
}

.dp-topbar-brand {
    display: flex;
    align-items: center;
    gap: 0.6rem;
}

.dp-topbar-title {
    font-size: 1.15rem;
    font-weight: 700;
    color: #FFFFFF;
    letter-spacing: -0.02em;
}

.dp-topbar-tagline {
    font-size: 0.82rem;
    color: #94A3B8;
    margin-left: 0.6rem;
    border-left: 1px solid rgba(255, 255, 255, 0.15);
    padding-left: 0.6rem;
}

.dp-topbar-center {
    flex: 1;
    display: flex;
    justify-content: center;
    padding: 0 1.5rem;
}

.dp-topbar-search {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    background: rgba(11, 15, 25, 0.7);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    padding: 0.45rem 1rem;
    width: 100%;
    max-width: 440px;
    font-size: 0.85rem;
    color: #94A3B8;
    transition: all 0.2s ease;
}

.dp-topbar-search:hover {
    border-color: rgba(99, 102, 241, 0.4);
    background: rgba(11, 15, 25, 0.9);
}

.dp-search-placeholder {
    color: #64748B;
    font-size: 0.82rem;
}

.dp-topbar-right {
    display: flex;
    align-items: center;
    gap: 1.25rem;
}

.dp-breadcrumbs {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.74rem;
    letter-spacing: 0.08em;
}

.dp-breadcrumb-active {
    color: #818CF8;
    font-weight: 700;
    text-shadow: 0 0 10px rgba(99, 102, 241, 0.5);
}

.dp-breadcrumb-idle {
    color: #475569;
}

.dp-breadcrumb-sep {
    color: #334155;
    margin: 0 0.35rem;
}

.dp-topbar-actions {
    display: flex;
    align-items: center;
    gap: 0.6rem;
}

.dp-icon-btn {
    width: 32px;
    height: 32px;
    border-radius: 8px;
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.08);
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.2s ease;
}

.dp-icon-btn:hover {
    background: rgba(99, 102, 241, 0.15);
    border-color: rgba(99, 102, 241, 0.35);
}

.dp-user-avatar {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: linear-gradient(135deg, #6366F1, #8B5CF6);
    color: #FFFFFF;
    font-weight: 700;
    font-size: 0.78rem;
    display: flex;
    align-items: center;
    justify-content: center;
    border: 1.5px solid rgba(255, 255, 255, 0.2);
}

/* --- Enterprise Cards --- */
.dp-card {
    background: rgba(17, 24, 39, 0.8) !important;
    backdrop-filter: blur(16px) !important;
    -webkit-backdrop-filter: blur(16px) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 12px !important;
    padding: 1.35rem 1.5rem !important;
    margin-bottom: 1.25rem !important;
    box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.4), inset 0 1px 0 0 rgba(255, 255, 255, 0.05) !important;
    transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
}

.dp-card:hover {
    border-color: rgba(99, 102, 241, 0.35) !important;
    box-shadow: 0 8px 30px -4px rgba(0, 0, 0, 0.5), 0 0 15px rgba(99, 102, 241, 0.12) !important;
}

/* --- KPI Cards --- */
.dp-kpi-card {
    background: rgba(17, 24, 39, 0.75);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 1.1rem 1.2rem;
    display: flex;
    flex-direction: column;
    gap: 0.3rem;
    transition: all 0.2s ease;
}

.dp-kpi-card:hover {
    border-color: rgba(99, 102, 241, 0.35);
    transform: translateY(-2px);
}

.dp-kpi-label {
    font-size: 0.82rem;
    color: #94A3B8;
    font-weight: 500;
}

.dp-kpi-value {
    font-size: 1.85rem;
    font-weight: 700;
    color: #F8FAFC;
    letter-spacing: -0.03em;
    line-height: 1.2;
}

.dp-kpi-trend-pos {
    font-size: 0.75rem;
    color: #34D399;
    font-family: 'JetBrains Mono', monospace;
    display: flex;
    align-items: center;
    gap: 0.25rem;
}

.dp-kpi-trend-neg {
    font-size: 0.75rem;
    color: #F87171;
    font-family: 'JetBrains Mono', monospace;
    display: flex;
    align-items: center;
    gap: 0.25rem;
}

/* --- Activity Feed Items --- */
.dp-activity-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.75rem 0;
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.dp-activity-item:last-child {
    border-bottom: none;
}

.dp-activity-title {
    font-size: 0.88rem;
    font-weight: 600;
    color: #F1F5F9;
}

.dp-activity-sub {
    font-size: 0.78rem;
    color: #64748B;
    margin-top: 0.15rem;
}

/* --- Drift Alert Card --- */
.dp-drift-alert-box {
    background: linear-gradient(135deg, rgba(239, 68, 68, 0.12) 0%, rgba(17, 24, 39, 0.8) 100%);
    border: 1px solid rgba(239, 68, 68, 0.35);
    border-radius: 12px;
    padding: 1.25rem 1.4rem;
    box-shadow: 0 0 20px rgba(239, 68, 68, 0.15);
}

.dp-drift-alert-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.6rem;
}

.dp-drift-alert-title {
    font-size: 1.02rem;
    font-weight: 700;
    color: #F87171;
}

.dp-drift-alert-desc {
    font-size: 0.85rem;
    color: #CBD5E1;
    line-height: 1.5;
    margin-bottom: 1rem;
}

/* --- System Health Card --- */
.dp-health-box {
    background: rgba(17, 24, 39, 0.75);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 1.1rem 1.25rem;
    margin-top: 1rem;
}

.dp-health-status {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    font-size: 0.88rem;
    font-weight: 600;
    color: #34D399;
    margin-top: 0.3rem;
}

.dp-pulse-dot {
    width: 9px;
    height: 9px;
    border-radius: 50%;
    background: #10B981;
    box-shadow: 0 0 10px #10B981;
    animation: dpPulse 2s infinite ease-in-out;
}

@keyframes dpPulse {
    0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
    70% { transform: scale(1.05); box-shadow: 0 0 0 8px rgba(16, 185, 129, 0); }
    100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
}

/* --- Badges & Micro-tags --- */
.dp-badge {
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
}

.dp-badge-review {
    background: rgba(239, 68, 68, 0.15) !important;
    color: #F87171 !important;
    border: 1px solid rgba(248, 113, 113, 0.4) !important;
}

/* --- Suggested Questions Pills --- */
.dp-pill-container {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin: 0.75rem 0 1.25rem 0;
}

.dp-suggested-pill {
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.1);
    color: #94A3B8;
    border-radius: 9999px;
    padding: 0.35rem 0.85rem;
    font-size: 0.8rem;
    cursor: pointer;
    transition: all 0.2s ease;
}

.dp-suggested-pill:hover {
    border-color: #6366F1;
    color: #F1F5F9;
    background: rgba(99, 102, 241, 0.12);
}

/* --- Data Tables --- */
.dp-table {
    width: 100%;
    border-collapse: collapse;
    margin: 1rem 0;
    font-size: 0.88rem;
}

.dp-table th {
    text-align: left;
    padding: 0.75rem 1rem;
    color: #94A3B8;
    font-weight: 600;
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.dp-table td {
    padding: 0.85rem 1rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.04);
    color: #E2E8F0;
}

.dp-table tr:hover td {
    background: rgba(255, 255, 255, 0.02);
}

/* --- Buttons --- */
.stButton > button {
    background: linear-gradient(135deg, #6366F1 0%, #4F46E5 100%) !important;
    color: #FFFFFF !important;
    border: 1px solid rgba(255, 255, 255, 0.15) !important;
    border-radius: 8px !important;
    padding: 0.45rem 1.25rem !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    box-shadow: 0 2px 10px rgba(99, 102, 241, 0.3) !important;
    transition: all 0.2s ease !important;
}

.stButton > button:hover {
    background: linear-gradient(135deg, #818CF8 0%, #6366F1 100%) !important;
    box-shadow: 0 4px 16px rgba(99, 102, 241, 0.45) !important;
    transform: translateY(-1px) !important;
}

/* --- Form Controls --- */
[data-baseweb="input"], [data-baseweb="select"] {
    background-color: #0F172A !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 8px !important;
}

[data-baseweb="input"]:focus-within, [data-baseweb="select"]:focus-within {
    border-color: #6366F1 !important;
    box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.25) !important;
}

/* --- Tabs --- */
[data-testid="stTabs"] {
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

/* --- Modals & Dialogs --- */
[data-testid="stDialog"] div[role="dialog"] {
    background: #0F172A !important;
    border: 1px solid rgba(99, 102, 241, 0.4) !important;
    border-radius: 16px !important;
    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.8), 0 0 30px rgba(99, 102, 241, 0.2) !important;
}

/* --- Timeline Nodes --- */
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
    font-size: 1.4rem;
    color: #818CF8;
    text-align: center;
    margin: 0.5rem 0;
    filter: drop-shadow(0 0 8px rgba(99, 102, 241, 0.5));
}
</style>
    """,
        unsafe_allow_html=True,
    )
