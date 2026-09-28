"""Memory Evolution page — Higher-order mental models, synthesized observations, and knowledge consolidation."""

from __future__ import annotations

import streamlit as st

from ui.adapters import get_backend
from ui.components._theme import inject_custom_css
from ui.components.dialogs import check_and_render_evidence_dialog
from ui.components.renders import render_mental_model_card, render_observation_card

backend = get_backend()
role = st.session_state.get("role") or "admin"

inject_custom_css()
check_and_render_evidence_dialog(backend, role)

st.title("🧬 Organizational Memory Evolution")
st.markdown(
    "<p style='color:#94A3B8; font-size:1.05rem;'>Observe how raw decisions consolidate over time into high-order observations, recurring failure patterns, and company-wide mental models.</p>",
    unsafe_allow_html=True,
)

# 1. Higher-Order Mental Models
st.markdown("### 🧠 Organizational Mental Models")
st.caption("Consolidated architectural heuristics synthesized across years of multi-project development:")

try:
    models = backend.list_mental_models(role)
    if models:
        for model in models:
            render_mental_model_card(model)
    else:
        st.info("💡 Observations are currently consolidating in the background. Check back shortly.")
except Exception as e:  # noqa: BLE001
    st.error(f"Failed to fetch mental models: {e}")

st.markdown("---")

# 2. Synthesized Observations with Topic Filter
st.markdown("### 🔭 Synthesized Observations & Evolutionary Trajectories")
st.caption(
    "Observations strengthen as evidence repeats across independent project lifecycles. Notice how evidence counts grow over time:"
)

col_topic, col_empty = st.columns([2, 3])
with col_topic:
    topic_choice = st.selectbox(
        "Filter by Topic Area", ["All Topics", "messaging", "cost", "redis", "debugging", "observability"], index=0
    )

topic_arg = None if topic_choice == "All Topics" else topic_choice

try:
    observations = backend.list_observations(role, topic_arg)
    if observations:
        for obs in observations:
            render_observation_card(obs)
    else:
        st.info("🔄 No observations currently match this topic or observations are still consolidating.")
except Exception as e:  # noqa: BLE001
    st.error(f"Failed to fetch observations: {e}")
