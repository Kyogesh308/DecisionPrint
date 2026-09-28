"""Ask page — The core DecisionPrint intelligence interface matching Stage 3."""

from __future__ import annotations

import html

import streamlit as st

from contracts import EpistemicType
from ui.adapters import get_backend
from ui.components import (
    inject_custom_css,
    render_html,
    render_sidebar_chrome,
    render_top_bar,
)
from ui.components._state import ChatTurn, init_session_state, run_guarded
from ui.components._theme import badge_html
from ui.components._viz import (
    _svg_bar_pair,
    _svg_ring,
    _svg_step_track,
    render_drift_gauge,
    render_traceability_meter,
)
from ui.components.dialogs import show_memory_trace_dialog

init_session_state()

if not st.session_state.get("_top_nav_active"):
    inject_custom_css()
    render_top_bar(active_stage="ANALYZE")
    render_sidebar_chrome()

backend = get_backend()
role = st.session_state.get("role") or "admin"
project_id = st.session_state.get("project_id") or "nova"

render_html("<h1 style='margin-bottom: 0.25rem;'>Ask your organization's memory</h1>")
render_html(
    "<p style='color:var(--dp-text-secondary); font-size:1.02rem; margin-bottom:1.5rem;'>Each question is answered from memory independently.</p>"
)


if not st.session_state.chat_turns:
    render_html(
        "<div style='margin-bottom:1rem; color:var(--dp-text-primary); font-weight:600;'>Suggested questions</div>"
    )
    cols = st.columns(4)
    if cols[0].button("Should Nova use Kafka?", use_container_width=True):
        st.session_state.ask_input = "Should Nova use Kafka for event streaming?"
    if cols[1].button("Why was GraphQL rejected?", use_container_width=True):
        st.session_state.ask_input = "Why was GraphQL rejected for internal APIs?"
    if cols[2].button("What happened after Cedar skipped backups?", use_container_width=True):
        st.session_state.ask_input = "What happened after Cedar skipped backups?"
    if cols[3].button("Has our Redis position changed?", use_container_width=True):
        st.session_state.ask_input = "Has our Redis position changed?"

# Render existing chat turns
for i, turn in enumerate(st.session_state.chat_turns):
    with st.chat_message("user"):
        st.write(turn.question)

    with st.chat_message("assistant"):
        if turn.error:
            st.error(turn.error)
            if "ScopeError" in turn.error:
                st.warning("🔒 " + turn.error)
            continue

        brief = turn.brief
        if not brief:
            st.info("No comparable decision found in memory")
            continue

        # Minimal answer
        answer = "Based on organizational memory, here's what was found."
        rec_claims = [c for c in brief.claims if c.epistemic_type == EpistemicType.recommendation]
        if brief.drift and brief.drift.summary:
            answer = brief.drift.summary
        elif rec_claims:
            answer = rec_claims[0].text

        st.markdown(f"**{html.escape(answer)}**")

        # Chips
        if brief.drift:
            lvl = brief.drift.level.value.upper()
            color_map = {"HIGH": "red", "MEDIUM": "yellow", "LOW": "gray"}
            c_badge = badge_html(lvl, color=color_map.get(lvl, "gray"))

            n_changed = sum(1 for i in brief.drift.delta.items if i.comparison.value == "changed")
            n_total = (
                len(brief.historical_decision.constraints)
                if brief.historical_decision.constraints
                else len(brief.drift.delta.items)
            )

            render_html(
                f"{c_badge} <span style='font-size:0.85rem; color:var(--dp-text-muted); margin-left:8px;'>{n_changed} of {n_total} premises changed</span>"
            )

        # Then vs Now
        if brief.drift and brief.drift.delta.items:
            st.markdown("### Then vs Now")
            items = sorted(brief.drift.delta.items, key=lambda x: not x.is_reason_linked)
            for item in items:
                col1, col2 = st.columns([1, 3])
                with col1:
                    rl = (
                        "<br><span style='font-size:0.75rem; color:var(--dp-text-muted);'>reason-linked</span>"
                        if item.is_reason_linked
                        else ""
                    )
                    render_html(f"<strong>{html.escape(item.key)}</strong>{rl}")
                with col2:
                    if item.old_value in ["true", "false"] and item.new_value in ["true", "false"]:
                        st.markdown(f"`{item.old_value}` → `{item.new_value}`")
                    elif item.old_value and item.old_value.isdigit() and item.new_value and item.new_value.isdigit():
                        st.components.v1.html(
                            _svg_bar_pair(
                                int(item.old_value),
                                int(item.new_value),
                                max_val=max(int(item.old_value), int(item.new_value)) * 2,
                            ),
                            height=40,
                        )
                    else:
                        st.components.v1.html(_svg_step_track(3, 1, 2), height=40)

        # Drift gauge
        if brief.drift:
            st.components.v1.html(render_drift_gauge(brief.drift.score, brief.drift.level.value), height=120)

        # Recommendation
        if rec_claims:
            st.markdown(f"*{html.escape(rec_claims[0].text)}*")

        # Tabs
        t1, t2, t3, t4, t5 = st.tabs(["Reasoning", "Evidence", "Epistemic", "Confidence", "Memory Trace"])

        with t1:
            st.write("Reasoning steps")
        with t2:
            st.write("Evidence list")
            st.components.v1.html(render_traceability_meter(0.85), height=80)
        with t3:
            st.write("Facts / Observations / Inferences")
        with t4:
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.components.v1.html(_svg_ring(brief.confidence.evidence_quality, "Quality"), height=100)
            with c2:
                st.components.v1.html(_svg_ring(brief.confidence.temporal_relevance, "Temporal"), height=100)
            with c3:
                st.components.v1.html(_svg_ring(brief.confidence.source_agreement, "Agreement"), height=100)
            with c4:
                st.components.v1.html(_svg_ring(brief.confidence.information_completeness, "Completeness"), height=100)
        with t5:
            if st.button("Inspect Memory Trace", key=f"trace_{i}"):
                try:
                    trace = backend.get_memory_trace(brief.query_id, role)
                    show_memory_trace_dialog(trace)
                except Exception as e:  # noqa: BLE001
                    st.error(f"Could not load trace: {e}")

# Handle input
user_input = st.chat_input("Ask about a decision, constraint or outcome…")
if st.session_state.get("ask_input"):
    user_input = st.session_state.ask_input
    st.session_state.ask_input = None

if user_input:
    # Add user message
    st.chat_message("user").write(user_input)

    # Process
    turn = ChatTurn(question=user_input)
    with st.chat_message("assistant"), st.spinner("Searching memory..."):
        brief = run_guarded(backend.ask_question, user_input, project_id, role)
        if brief:
            turn.brief = brief
            turn.query_id = brief.query_id
            st.rerun()
        else:
            turn.error = "Error querying memory or access denied"

    st.session_state.chat_turns.append(turn)
    st.rerun()
