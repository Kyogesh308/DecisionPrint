"""Design tokens — single source of truth for UI colours and badges."""

# Epistemic types
EPISTEMIC_COLORS = {
    "fact": {"bg": "#1e3a5f", "text": "#60a5fa", "label": "FACT"},
    "observation": {"bg": "#1a3a3a", "text": "#5eead4", "label": "OBSERVATION"},
    "inference": {"bg": "#3d2e1a", "text": "#fbbf24", "label": "INFERENCE"},
    "recommendation": {"bg": "#2d1b4e", "text": "#a78bfa", "label": "RECOMMENDATION"},
}

# Drift levels
DRIFT_COLORS = {
    "none": {"bg": "#1a3a2a", "text": "#4ade80", "label": "NO DRIFT"},
    "low": {"bg": "#3d3a1a", "text": "#facc15", "label": "LOW"},
    "medium": {"bg": "#3d2a1a", "text": "#fb923c", "label": "MEDIUM"},
    "high": {"bg": "#3d1a1a", "text": "#f87171", "label": "HIGH"},
}

# Comparison badges
COMPARISON_COLORS = {
    "same": {"bg": "#2a2a2a", "text": "#9ca3af", "label": "Same"},
    "changed": {"bg": "#3d1a1a", "text": "#f87171", "label": "Changed"},
    "newly_present": {"bg": "#3d2a1a", "text": "#fb923c", "label": "New"},
    "unknown": {"bg": "#2a2a2a", "text": "#6b7280", "label": "Unknown"},
    "incomparable": {"bg": "#2a2a2a", "text": "#6b7280", "label": "N/A"},
}

# Causal link labels
CAUSAL_COLORS = {
    "explicit_causal_link": {"bg": "#1a2a5f", "text": "#818cf8", "label": "EXPLICIT CAUSAL LINK"},
    "strong_evidence": {"bg": "#1a3a3a", "text": "#5eead4", "label": "STRONG EVIDENCE"},
    "possible_causal_link": {"bg": "#3d2e1a", "text": "#fbbf24", "label": "POSSIBLE LINK"},
    "fact": {"bg": "#1e3a5f", "text": "#60a5fa", "label": "FACT"},
    "none": {"bg": "#2a2a2a", "text": "#6b7280", "label": ""},  # never render
}

# Decision status
STATUS_COLORS = {
    "active": {"bg": "#1a3a2a", "text": "#4ade80", "label": "Active"},
    "superseded": {"bg": "#3d2a1a", "text": "#fb923c", "label": "Superseded"},
    "reconsidered": {"bg": "#1e3a5f", "text": "#60a5fa", "label": "Reconsidered"},
}


def badge_html(category: str, value: str) -> str:
    """Return styled HTML badge for the given category and value."""
    lookup = {
        "epistemic": EPISTEMIC_COLORS,
        "drift": DRIFT_COLORS,
        "comparison": COMPARISON_COLORS,
        "causal": CAUSAL_COLORS,
        "status": STATUS_COLORS,
    }
    colors = lookup.get(category, {}).get(value, {"bg": "#2a2a2a", "text": "#9ca3af", "label": value})
    if not colors.get("label"):
        return ""  # never render empty labels (e.g. causal 'none')
    return (
        f'<span class="dp-badge" style="background:{colors["bg"]};color:{colors["text"]};'
        f"padding:2px 10px;border-radius:12px;font-size:0.75rem;font-weight:600;"
        f'letter-spacing:0.05em;">{colors["label"]}</span>'
    )
