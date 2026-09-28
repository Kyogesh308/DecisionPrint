"""Decision Explorer page — Searchable decision repository and review queue matching Screen 5."""

from __future__ import annotations

import html

import streamlit as st

from contracts import DecisionFilter, DecisionStatus
from ui.adapters import get_backend
from ui.components import (
    badge_html,
    inject_custom_css,
    render_confidence_breakdown,
    render_decision_card,
    render_html,
    render_sidebar_chrome,
    render_top_bar,
)
from ui.components._state import init_session_state, run_guarded
from ui.components.dialogs import check_and_render_evidence_dialog

init_session_state()

if not st.session_state.get("_top_nav_active"):
    inject_custom_css()
    render_top_bar(active_stage="ANALYZE")
    render_sidebar_chrome()

backend = get_backend()
role = st.session_state.get("role") or "admin"
check_and_render_evidence_dialog(backend, role)

# 1. Header
render_html(
    """
    <div style='margin-bottom: 1.25rem;'>
        <h1 style='margin-bottom: 0.25rem;'>Decision Explorer</h1>
        <p style='color:var(--muted); font-size:1.02rem; margin:0;'>
            Search and filter architectural decisions, historical context, and verification status.
        </p>
    </div>
    """
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
        if st.button("Reset", use_container_width=True):
            st.rerun()

    # Search Bar
    s_col, b_col = st.columns([4, 1])
    with s_col:
        initial_search = st.session_state.get("global_search", "")
        text_q = st.text_input(
            "Search Text",
            value=initial_search,
            placeholder="Search decisions, keywords, or tags...",
            key="explorer_search_text",
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
        decisions = run_guarded(backend.search_decisions, d_filter, role)

        # Build entire card + table as ONE compact string
        rows_parts = []
        for dec in decisions:
            tech_chips = " ".join([f"<code>{html.escape(t)}</code>" for t in dec.technologies]) or "<code>general</code>"
            st_badge = badge_html("status", dec.status.value)
            date_s = dec.date.strftime("%Y-%m-%d") if dec.date else "2026-05-12"
            rows_parts.append(
                f"""
                <tr>
                    <td><strong>{html.escape(dec.title)}</strong><div class='dp-id-text'>{html.escape(dec.decision_id)}</div></td>
                    <td><strong>{html.escape(dec.project_id.upper())}</strong></td>
                    <td>{tech_chips}</td>
                    <td><span class='dp-id-text'>{date_s}</span></td>
                    <td>{st_badge}</td>
                </tr>
                """
            )

        rows_html = "".join(rows_parts)
        card_table_fragment = f"""
        <div class='dp-card'>
            <h3>Indexed Decision Records ({len(decisions)})</h3>
            <div class='dp-table-container'>
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
                        {rows_html}
                    </tbody>
                </table>
            </div>
        </div>
        """
        render_html(card_table_fragment)

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
        review_items = run_guarded(backend.list_review_queue, role)
        if review_items:
            for item in review_items:
                render_html(
                    f"""
                    <div class='dp-card'>
                        <h4><code>{html.escape(item.decision_id)}</code>: {html.escape(item.title)}</h4>
                        <p><strong>Flagged Reason:</strong> <span style='color:var(--yellow);'>{html.escape(item.reason)}</span></p>
                    </div>
                    """
                )

                if item.confidence:
                    render_confidence_breakdown(item.confidence)

                col_appr, col_rej = st.columns([1, 4])
                with col_appr:
                    # ponytail: hardcoded for demo, wire to approve endpoint later
                    if st.button("✅ Confirm Extraction", key=f"appr_{item.decision_id}"):
                        st.success(f"Decision {item.decision_id} confirmed and validated!")
                with col_rej:
                    # ponytail: hardcoded for demo, wire to reject endpoint later
                    if st.button("❌ Reject Extraction", key=f"rej_{item.decision_id}"):
                        st.info(f"Decision {item.decision_id} queued for manual correction.")
        else:
            st.success("✅ The review queue is clear! All extractions meet high confidence thresholds.")
    except Exception as e:  # noqa: BLE001
        st.error(f"Failed to fetch review queue: {e}")
