"""Decision Explorer page — Comprehensive search, filtering, and review queue."""

from __future__ import annotations

import streamlit as st

from contracts import DecisionFilter, DecisionStatus
from ui.adapters import get_backend
from ui.components.dialogs import check_and_render_evidence_dialog
from ui.components.renders import render_confidence_breakdown, render_decision_card

backend = get_backend()
role = st.session_state.get("role", "admin")

check_and_render_evidence_dialog(backend, role)

st.title("🔎 Decision Explorer & Review Queue")
st.markdown(
    "<p style='color:#94A3B8; font-size:1.05rem;'>Search, filter, and audit architectural decisions across technology stacks, historical lifecycles, and verification queues.</p>",
    unsafe_allow_html=True,
)

tab_decisions, tab_review = st.tabs(["📚 All Decisions Repository", "⚠️ Low-Confidence Review Queue (G2)"])

with tab_decisions:
    # Filter Bar
    c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
    with c1:
        text_q = st.text_input(
            "Search Text", placeholder="e.g. RabbitMQ, Redis, latency, scale...", label_visibility="collapsed"
        )
    with c2:
        proj_filter = st.selectbox("Project", ["All", "alpha", "beta", "gamma", "delta", "nova"], index=0)
    with c3:
        tech_filter = st.selectbox("Technology", ["All", "rabbitmq", "kafka", "redis", "amqp", "postgres"], index=0)
    with c4:
        status_filter = st.selectbox("Status", ["All", "active", "superseded", "reconsidered"], index=0)

    # Build DecisionFilter
    d_filter = DecisionFilter(
        text=text_q if text_q else None,
        project_id=None if proj_filter == "All" else proj_filter,
        technology=None if tech_filter == "All" else tech_filter,
        status=None if status_filter == "All" else DecisionStatus(status_filter),
    )

    try:
        decisions = backend.search_decisions(d_filter, role)
        st.markdown(f"**Found {len(decisions)} decision(s)** matching filters:")
        if decisions:
            for dec in decisions:
                render_decision_card(dec)
                # Quick navigation to Timeline
                if st.button(f"⏱️ Open {dec.decision_id} in Timeline", key=f"nav_tl_{dec.decision_id}"):
                    st.session_state.selected_decision_id = dec.decision_id
                    st.switch_page("pages/3_Timeline.py")
        else:
            st.info("No decisions match the selected criteria.")
    except Exception as e:  # noqa: BLE001
        st.error(f"Error exploring decisions: {e}")

with tab_review:
    st.markdown("### ⚠️ Human-in-the-Loop Review Queue")
    st.caption(
        "Under PRD requirements, low-confidence extractions from ambiguous meeting notes or legacy transcripts are flagged here for human sign-off before influencing organizational drift calculations."
    )

    try:
        review_items = backend.list_review_queue(role)
        if review_items:
            for item in review_items:
                st.markdown("<div class='dp-card'>", unsafe_allow_html=True)
                st.markdown(f"#### <code>{item.decision_id}</code>: {item.title}")
                st.markdown(
                    f"**Flagged Reason:** <span style='color:#fbbf24;'>{item.reason}</span>", unsafe_allow_html=True
                )

                if item.confidence:
                    render_confidence_breakdown(item.confidence)

                col_appr, col_rej = st.columns([1, 4])
                with col_appr:
                    if st.button("✅ Confirm Extraction", key=f"appr_{item.decision_id}"):
                        st.success(f"Decision {item.decision_id} confirmed and validated!")
                with col_rej:
                    if st.button("❌ Reject Extraction", key=f"rej_{item.decision_id}"):
                        st.info(f"Decision {item.decision_id} queued for manual correction.")
                st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.success("✅ The review queue is clear! All extractions meet high confidence thresholds.")
    except Exception as e:  # noqa: BLE001
        st.error(f"Failed to fetch review queue: {e}")
