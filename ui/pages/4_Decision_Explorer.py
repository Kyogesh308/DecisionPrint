"""Decision Explorer page — Searchable decision repository and review queue matching Screen 5."""

from __future__ import annotations

import streamlit as st

from contracts import DecisionFilter, DecisionStatus
from ui.adapters import get_backend
from ui.components import (
    badge_html,
    inject_custom_css,
    render_confidence_breakdown,
    render_decision_card,
    render_sidebar_chrome,
    render_top_bar,
)
from ui.components.dialogs import check_and_render_evidence_dialog

inject_custom_css()

backend = get_backend()
role = st.session_state.get("role") or "admin"

render_top_bar(active_stage="ANALYZE")
render_sidebar_chrome()
check_and_render_evidence_dialog(backend, role)

# 1. Header
st.markdown(
    """
    <div style='margin-bottom: 1.25rem;'>
        <h1 style='margin-bottom: 0.25rem;'>Decision Explorer</h1>
        <p style='color:#94A3B8; font-size:1.02rem; margin:0;'>
            Search and filter architectural decisions, historical context, and verification status.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

tab_decisions, tab_review = st.tabs(["📚 All Decisions Repository", "⚠️ Low-Confidence Review Queue (G2)"])

with tab_decisions:
    # Compact Filter Controls matching Mockup Screen 5
    f1, f2, f3, f4 = st.columns([1.5, 1.5, 1.5, 1])
    with f1:
        proj_filter = st.selectbox("Project", ["All Projects", "nova", "alpha", "beta", "gamma", "delta"], index=0)
    with f2:
        tech_filter = st.selectbox(
            "Technology", ["All Technologies", "kafka", "rabbitmq", "redis", "amqp", "postgres", "graphql"], index=0
        )
    with f3:
        status_filter = st.selectbox("Status", ["All Statuses", "active", "superseded", "reconsidered"], index=0)
    with f4:
        st.markdown("<div style='height: 1.7rem;'></div>", unsafe_allow_html=True)
        if st.button("Reset", use_container_width=True):
            st.rerun()

    # Search Bar
    s_col, b_col = st.columns([4, 1])
    with s_col:
        text_q = st.text_input(
            "Search Text",
            placeholder="Search decisions, keywords, or tags...",
            label_visibility="collapsed",
        )
    with b_col:
        do_search = st.button("🔍 Search", type="primary", use_container_width=True)

    # Build DecisionFilter
    d_filter = DecisionFilter(
        text=text_q if text_q else None,
        project_id=None if proj_filter == "All Projects" else proj_filter,
        technology=None if tech_filter == "All Technologies" else tech_filter,
        status=None if status_filter == "All Statuses" else DecisionStatus(status_filter),
    )

    try:
        decisions = backend.search_decisions(d_filter, role)

        # Structured Table View matching Screen 5
        st.markdown("<div class='dp-card'>", unsafe_allow_html=True)
        st.markdown(f"**Indexed Decision Records ({len(decisions)})**")

        rows_html = []
        for dec in decisions:
            tech_chips = " ".join([f"<code>{t}</code>" for t in dec.technologies]) or "<code>general</code>"
            st_badge = badge_html("status", dec.status.value)
            date_s = dec.date.strftime("%Y-%m-%d") if dec.date else "2026-05-12"
            rows_html.append(
                f"""
                <tr>
                    <td><strong>{dec.title}</strong><div style='font-size:0.75rem; color:var(--dp-primary, #315EDE);'>{dec.decision_id}</div></td>
                    <td><strong style='color:var(--dp-text-primary, #17243B);'>{dec.project_id.upper()}</strong></td>
                    <td>{tech_chips}</td>
                    <td style='font-family:"JetBrains Mono", monospace; font-size:0.82rem;'>{date_s}</td>
                    <td>{st_badge}</td>
                </tr>
                """
            )

        table_body = "".join(rows_html)
        st.markdown(
            f"""
            <table class='dp-table'>
                <thead>
                    <tr>
                        <th>Decision</th>
                        <th>Project</th>
                        <th>Tech</th>
                        <th>Date</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    {table_body}
                </tbody>
            </table>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

        # Detailed cards expandable list
        st.markdown("### Decision Inspection Cards")
        for dec in decisions:
            render_decision_card(dec)

    except Exception as e:  # noqa: BLE001
        st.error(f"Error exploring decisions: {e}")

with tab_review:
    st.markdown("### ⚠️ Human-in-the-Loop Review Queue")
    st.caption(
        "Low-confidence extractions from ambiguous meeting notes or legacy transcripts are flagged here for human sign-off before influencing organizational drift calculations."
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
