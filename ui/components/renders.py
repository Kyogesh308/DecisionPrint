"""UI components — pure rendering of contract models."""

from __future__ import annotations

import streamlit as st

from contracts import (
    BriefClaim,
    ConfidenceBreakdown,
    ConstraintDelta,
    Decision,
    DecisionBrief,
    DriftResult,
    EvidenceExcerpt,
    IngestResult,
    MemoryOverview,
    MemoryTrace,
    MentalModelView,
    ObservationView,
    OutcomeChain,
    TimelineEvent,
)
from ui.components._theme import (
    DRIFT_COLORS,
    badge_html,
)


def render_memory_overview(overview: MemoryOverview) -> None:
    """Render hero section with memory metrics and last updated date."""
    st.markdown("<div class='dp-hero'>", unsafe_allow_html=True)
    st.markdown(f"## 🧠 Memory learned from {overview.project_count} historical projects")
    if overview.last_updated:
        st.markdown(
            f"<p style='color:#94A3B8;'>Last consolidated: {overview.last_updated.strftime('%Y-%m-%d %H:%M')}</p>",
            unsafe_allow_html=True,
        )

    if overview.project_count == 0 and overview.source_count == 0:
        st.info("No memory ingested yet. Start by ingesting historical project documents.")
    else:
        c1, c2, c3, c4, c5, c6 = st.columns(6)
        c1.metric("Projects", overview.project_count)
        c2.metric("Sources", overview.source_count)
        c3.metric("Decisions", overview.decision_count)
        c4.metric("Facts", overview.fact_count)
        c5.metric("Observations", overview.observation_count)
        c6.metric("Mental Models", overview.mental_model_count)
    st.markdown("</div>", unsafe_allow_html=True)


def render_decision_card(decision: Decision) -> None:
    """Render a detailed card for an architectural decision."""
    st.markdown("<div class='dp-card'>", unsafe_allow_html=True)

    status_badge = badge_html("status", decision.status.value)
    review_badge = "<span class='dp-badge dp-badge-review'>Needs Review</span>" if decision.needs_review else ""

    date_str = decision.date.strftime("%Y-%m-%d") if decision.date else ""
    st.markdown(f"### {decision.title} {status_badge} {review_badge}", unsafe_allow_html=True)
    st.markdown(
        f"<p class='dp-timeline-date'>{date_str} · Project: <strong>{decision.project_id.upper()}</strong> · Decision ID: <code>{decision.decision_id}</code></p>",
        unsafe_allow_html=True,
    )
    st.markdown(f"**Statement:** {decision.statement}")
    st.markdown(f"**Selected Option:** `{decision.selected_option}`")

    if decision.reasons:
        st.markdown("**Core Reasons:**")
        for reason in decision.reasons:
            st.markdown(f"- {reason}")

    if decision.constraints:
        st.markdown("**Key Premises / Constraints:**")
        for c in decision.constraints:
            link_icon = f" ⚡ <em>(Reason-linked, weight {c.weight:.2f})</em>" if c.is_reason_linked else ""
            c_badge = badge_html("comparison", c.comparison.value)
            old_str = c.old_value if c.old_value is not None else "None"
            new_str = c.new_value if c.new_value is not None else "None"
            st.markdown(
                f"- **{c.key}**: `{old_str}` → `{new_str}` {c_badge}{link_icon}",
                unsafe_allow_html=True,
            )

    if decision.alternatives:
        st.markdown("**Alternatives Considered:**")
        for alt in decision.alternatives:
            disp_badge = badge_html("status", "active" if alt.disposition.value == "selected" else "superseded")
            reasons_str = f" — {', '.join(alt.reasons)}" if alt.reasons else ""
            st.markdown(f"- **{alt.name}** {disp_badge}{reasons_str}", unsafe_allow_html=True)

    if decision.technologies:
        techs = " ".join([f"`{t}`" for t in decision.technologies])
        st.markdown(f"**Technologies:** {techs}")

    if decision.source_ids:
        st.markdown("**Evidence Sources:**")
        cols = st.columns(min(len(decision.source_ids), 4))
        for idx, s_id in enumerate(decision.source_ids):
            with cols[idx % len(cols)]:
                if st.button(f"📄 {s_id}", key=f"src_{decision.decision_id}_{s_id}"):
                    st.session_state.evidence_ref = s_id

    st.markdown("</div>", unsafe_allow_html=True)


def render_constraint_delta_table(delta: ConstraintDelta) -> None:
    """Render a table comparing old and new constraints, highlighting reason-linked ones."""
    if not delta.items:
        st.info("No constraint changes detected.")
        return

    st.markdown("<div class='dp-card'>", unsafe_allow_html=True)
    st.markdown("### ⚖️ Constraint Delta (Historical Premise → Current Reality)")

    sorted_items = sorted(delta.items, key=lambda x: not x.is_reason_linked)

    for item in sorted_items:
        border_style = (
            "border-left: 3px solid #6366F1; padding-left: 14px; background: rgba(99, 102, 241, 0.08); border-radius: 6px;"
            if item.is_reason_linked
            else "padding-left: 14px; border-left: 3px solid transparent;"
        )
        c_badge = badge_html("comparison", item.comparison.value)
        weight_text = (
            f"<span style='color:#a78bfa; font-weight:600;'>⚡ Reason-linked (Weight {item.weight:.2f})</span>"
            if item.is_reason_linked
            else "<span style='color:#64748B;'>Standard constraint</span>"
        )

        old_v = item.old_value if item.old_value is not None else "—"
        new_v = item.new_value if item.new_value is not None else "—"

        st.markdown(
            f"<div style='{border_style} margin-bottom: 10px; padding-top: 6px; padding-bottom: 6px;'>",
            unsafe_allow_html=True,
        )
        st.markdown(f"**{item.key}** {c_badge} · {weight_text}", unsafe_allow_html=True)
        st.markdown(
            f"<span style='color:#94A3B8;'>Old Premise:</span> <code>{old_v}</code> ➔ <span style='color:#38BDF8;'>Current:</span> <code>{new_v}</code>",
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


def render_drift_card(drift: DriftResult) -> None:
    """Render a prominent banner showing context drift severity."""
    lvl = drift.level.value.lower()
    colors = DRIFT_COLORS.get(lvl, DRIFT_COLORS["low"])
    bg_color = colors["bg"]
    text_color = colors["text"]

    border_pulse = (
        "box-shadow: 0 0 20px rgba(239, 68, 68, 0.35); border: 1.5px solid #EF4444;"
        if lvl == "high"
        else f"border: 1px solid {text_color};"
    )

    rec_badge = (
        "<span style='background: rgba(239, 68, 68, 0.2); color:#F87171; border: 1px solid rgba(239, 68, 68, 0.4); padding:4px 12px; border-radius:9999px; font-weight:700; font-size:0.8rem; letter-spacing:0.04em;'>⚠️ RECONSIDERATION WARRANTED</span>"
        if drift.reconsideration_warranted
        else "<span style='background: rgba(34, 197, 94, 0.2); color:#4ADE80; border: 1px solid rgba(34, 197, 94, 0.4); padding:4px 12px; border-radius:9999px; font-weight:700; font-size:0.8rem; letter-spacing:0.04em;'>✅ ORIGINAL DECISION HOLDS</span>"
    )

    st.markdown(
        f"""
    <div class='dp-card' style='background-color: {bg_color}; {border_pulse} padding: 1.5rem; margin-bottom: 1.5rem;'>
        <div style='display:flex; justify-content:space-between; align-items:center;'>
            <h3 style='margin:0; color:{text_color} !important;'>DRIFT LEVEL: {badge_html("drift", drift.level.value)}</h3>
            <div>{rec_badge}</div>
        </div>
        <p style='font-size: 1.4em; margin: 0.5rem 0; font-weight: 700; color:{text_color};'>
            Drift Score: {drift.score * 100:.1f}%
        </p>
        <p style='margin-bottom:0; color:#E2E8F0; font-size:1.05rem;'>{drift.summary}</p>
    </div>
    """,
        unsafe_allow_html=True,
    )


def render_epistemic_section(title: str, claims: list[BriefClaim]) -> None:
    """Render claims grouped by epistemic type."""
    if not claims:
        return

    st.markdown(f"#### {title}")
    for claim in claims:
        badge = badge_html("epistemic", claim.epistemic_type.value)
        srcs = " ".join([f"`{sid}`" for sid in claim.source_ids])
        src_markup = f" <span style='color:#94A3B8;'>[{srcs}]</span>" if srcs else ""
        st.markdown(f"- {badge} {claim.text}{src_markup}", unsafe_allow_html=True)


def render_confidence_breakdown(confidence: ConfidenceBreakdown) -> None:
    """Render four horizontal bars showing confidence dimensions."""
    st.markdown("<div class='dp-card'>", unsafe_allow_html=True)
    st.markdown("### 📊 Multi-Dimensional Confidence Breakdown")
    st.caption(
        "DecisionPrint never collapses confidence to a single synthetic percentage. Each dimension is audited independently:"
    )

    metrics = [
        ("Evidence Quality", confidence.evidence_quality, "Direct primary sources vs. second-hand commentary"),
        ("Temporal Relevance", confidence.temporal_relevance, "Freshness relative to organization's current scale"),
        ("Source Agreement", confidence.source_agreement, "Consensus across ADRs, meeting transcripts, and retros"),
        (
            "Information Completeness",
            confidence.information_completeness,
            "Coverage across all decision constraint premises",
        ),
    ]

    cols = st.columns(4)
    for idx, (label, val, desc) in enumerate(metrics):
        score = val if val is not None else 0.0
        with cols[idx]:
            st.metric(label, f"{score * 100:.0f}%")
            st.progress(score)
            st.caption(desc)

    st.markdown("</div>", unsafe_allow_html=True)


def render_brief(brief: DecisionBrief) -> None:
    """Render the master Decision Brief view combining multiple components."""
    # 1. Current context strip
    if brief.current_constraints:
        st.markdown(
            "<div class='dp-card' style='padding: 0.8rem 1.2rem; margin-bottom: 1.5rem;'>", unsafe_allow_html=True
        )
        st.markdown("**Active Project Context Constraints:**")
        chips = " &nbsp;|&nbsp; ".join([f"<code>{k} = {v}</code>" for k, v in brief.current_constraints.items()])
        st.markdown(chips, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # 2. Two columns: Historical Decision | Constraint Delta
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🏛️ Historical Memory")
        if brief.historical_decision:
            render_decision_card(brief.historical_decision)
        else:
            st.info("No relevant historical decision found.")
    with col2:
        if brief.drift and brief.drift.delta:
            render_constraint_delta_table(brief.drift.delta)
        else:
            st.info("No constraint delta available.")

    # 3. Drift banner
    if brief.drift:
        render_drift_card(brief.drift)

    # 4. Epistemic sections (Fact, Observation, Inference, Recommendation)
    st.markdown("<div class='dp-card'>", unsafe_allow_html=True)
    st.markdown("### 🧭 Epistemic Knowledge Base")

    facts = [c for c in brief.claims if c.epistemic_type.value == "fact"]
    observations = [c for c in brief.claims if c.epistemic_type.value == "observation"]
    inferences = [c for c in brief.claims if c.epistemic_type.value == "inference"]
    recommendations = [c for c in brief.claims if c.epistemic_type.value == "recommendation"]

    if facts:
        render_epistemic_section("Documented Facts", facts)
    if observations:
        render_epistemic_section("Synthesized Observations", observations)
    if inferences:
        render_epistemic_section("Logical Inferences", inferences)
    if recommendations:
        render_epistemic_section("Actionable Recommendations", recommendations)

    st.markdown("</div>", unsafe_allow_html=True)

    # 5. Confidence breakdown
    if brief.confidence:
        render_confidence_breakdown(brief.confidence)

    # 6. Sources list
    if brief.source_ids:
        st.markdown("<div class='dp-card'>", unsafe_allow_html=True)
        st.markdown("### 📚 Grounding Evidence Sources")
        st.caption("Click any source to inspect the verbatim excerpt recorded in memory:")
        cols = st.columns(min(len(brief.source_ids), 4))
        for idx, sid in enumerate(brief.source_ids):
            with cols[idx % len(cols)]:
                if st.button(f"🔍 View {sid}", key=f"brief_src_{sid}"):
                    st.session_state.evidence_ref = sid
        st.markdown("</div>", unsafe_allow_html=True)


def render_evidence_panel(evidence: EvidenceExcerpt) -> None:
    """Render an evidence excerpt suitable for a dialog."""
    st.markdown("<div class='dp-card'>", unsafe_allow_html=True)
    st.markdown(f"### Evidence Excerpt: <code>{evidence.source_id}</code>", unsafe_allow_html=True)
    date_str = evidence.date.strftime("%Y-%m-%d") if evidence.date else "Undated"
    kind_badge = badge_html("epistemic", evidence.kind.value)
    st.markdown(
        f"<p class='dp-timeline-date'>{date_str} · Project: <strong>{evidence.project_id.upper()}</strong> · {kind_badge}</p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""<blockquote style='border-left: 3px solid #6366F1; padding: 1rem 1.4rem; background: rgba(99, 102, 241, 0.08); border-radius: 8px; font-style: italic; color: #F1F5F9; border: 1px solid rgba(99, 102, 241, 0.2);'>
        "{evidence.excerpt}"
        </blockquote>""",
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)


def render_decision_timeline(events: list[TimelineEvent]) -> None:
    """Render a vertical timeline of decision evolution events."""
    st.markdown("<div class='dp-card'>", unsafe_allow_html=True)
    st.markdown("### ⏱️ Decision Evolution Timeline")

    ordered_events = sorted(events, key=lambda x: x.occurred_at)
    for event in ordered_events:
        status_b = badge_html("status", event.status.value)
        kind_title = event.kind.value.replace("_", " ").upper()
        date_str = event.occurred_at.strftime("%Y-%m-%d")

        st.markdown("<div class='dp-timeline-item'>", unsafe_allow_html=True)
        st.markdown("<div class='dp-timeline-dot'></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='dp-timeline-date'>{date_str} · {kind_title}</div>", unsafe_allow_html=True)
        st.markdown(f"**{event.title}** {status_b}", unsafe_allow_html=True)
        st.markdown(f"<p style='color:#CBD5E1;'>{event.summary}</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


def render_ingest_result(result: IngestResult) -> None:
    """Render the result of an ingest operation."""
    color = (
        "#4ade80" if result.status.value == "success" else "#fb923c" if result.status.value == "partial" else "#f87171"
    )

    st.markdown(f"<div class='dp-card' style='border: 1px solid {color};'>", unsafe_allow_html=True)
    st.markdown(
        f"<h3 style='color: {color} !important;'>🚀 Memory Updated: {result.status.value.upper()}</h3>",
        unsafe_allow_html=True,
    )
    st.markdown(f"**Source Ingested:** <code>{result.source_id}</code>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    c1.metric("Memories Created", result.memories_created)
    c2.metric("Decisions Extracted", result.decisions_extracted)
    c3.metric("Outcomes Linked", result.outcomes_linked)

    if result.needs_review_ids:
        st.warning(f"⚠️ Low confidence extraction queued for review: {', '.join(result.needs_review_ids)}")

    if result.warnings:
        for w in result.warnings:
            st.caption(f"⚠️ {w}")

    st.markdown("</div>", unsafe_allow_html=True)


def render_observation_card(obs: ObservationView) -> None:
    """Render a card detailing an observation and its evolution."""
    st.markdown("<div class='dp-card'>", unsafe_allow_html=True)
    st.markdown(f"### 🔭 {obs.statement}")
    st.markdown(
        f"<span class='dp-badge' style='background: rgba(20, 184, 166, 0.15); color: #2DD4BF; border: 1px solid rgba(20, 184, 166, 0.3);'>Supporting Evidence: {obs.evidence_count} sources</span>",
        unsafe_allow_html=True,
    )

    first_s = obs.first_seen.strftime("%Y-%m-%d") if obs.first_seen else "—"
    last_u = obs.last_updated.strftime("%Y-%m-%d") if obs.last_updated else "—"
    st.markdown(
        f"<p class='dp-timeline-date'>First identified: {first_s} · Last reinforced: {last_u}</p>",
        unsafe_allow_html=True,
    )

    if obs.supporting_source_ids:
        chips = " ".join([f"`{sid}`" for sid in obs.supporting_source_ids])
        st.markdown(f"**Grounded in Sources:** {chips}")

    if obs.history:
        st.markdown("**Observation Evolution (Reinforcement across projects):**")
        for h in obs.history:
            h_date = h.timestamp.strftime("%Y-%m-%d") if h.timestamp else ""
            st.markdown(
                f"- 📈 <strong>{h_date}</strong>: Evidence grew to <code>{h.evidence_count}</code> occurrences — <em>{h.summary}</em>",
                unsafe_allow_html=True,
            )

    st.markdown("</div>", unsafe_allow_html=True)


def render_mental_model_card(model: MentalModelView) -> None:
    """Render a card detailing a mental model."""
    st.markdown("<div class='dp-card'>", unsafe_allow_html=True)
    st.markdown(f"### 🧠 Mental Model: {model.name}")
    st.markdown(f"<p style='font-size:1.1rem; color:#E2E8F0;'>{model.content}</p>", unsafe_allow_html=True)
    refreshed_str = model.last_refreshed.strftime("%Y-%m-%d") if model.last_refreshed else "—"
    st.markdown(
        f"<p class='dp-timeline-date'>Consolidated: {refreshed_str} · Synthesized from <strong>{model.evidence_count}</strong> observations</p>",
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)


def render_memory_trace_drawer(trace: MemoryTrace) -> None:
    """Render the memory retrieval trace in human terms (for a dialog or drawer)."""
    st.markdown(f"### 🔍 Hindsight Memory Trace: <code>{trace.query_id}</code>", unsafe_allow_html=True)
    st.caption("Full auditability: inspect how Hindsight recalled and connected memories to generate the brief:")

    t1, t2, t3 = st.tabs(
        ["1. Retained Primary Sources", "2. Recalled Memories", "3. Active Mental Models & Observations"]
    )

    with t1:
        if trace.retained:
            for src in trace.retained:
                st.markdown(f"- 📄 **{src.source_id}**: {src.title}")
        else:
            st.info("No primary sources retained directly in context window.")

    with t2:
        if trace.recalled:
            for mem in trace.recalled:
                tags = " ".join([f"`{e}`" for e in mem.entities])
                st.markdown(
                    f"- 💡 **{mem.kind}** (Relevance: <code>{mem.relevance * 100:.0f}%</code>) — Entities: {tags}",
                    unsafe_allow_html=True,
                )
        else:
            st.info("No synthetic memories recalled.")

    with t3:
        if trace.observations_used:
            for obs in trace.observations_used:
                st.markdown(f"- 🔭 {obs}")
        else:
            st.info("No higher-order observations linked to this query.")


def render_outcome_chain(chain: OutcomeChain) -> None:
    """Render a linear outcome chain visualization with causal badges."""
    st.markdown("<div class='dp-card'>", unsafe_allow_html=True)
    st.markdown(
        f"### 🔗 Decision Consequence Chain (Decision ID: <code>{chain.decision_id}</code>)", unsafe_allow_html=True
    )
    st.caption(
        "Auditing the downstream consequences of architectural choices through postmortems and incident records:"
    )

    for i, step in enumerate(chain.steps):
        step_date = step.date.strftime("%Y-%m-%d") if step.date else "Undated"
        st.markdown(
            f"""
        <div class='dp-card' style='background: rgba(17, 24, 39, 0.85); border-left: 4px solid #6366F1; padding: 1rem 1.4rem; margin-bottom: 0.5rem;'>
            <div style='font-size:0.85rem; color:#94A3B8; font-family: "JetBrains Mono", monospace;'>Step {i + 1} · {step_date}</div>
            <h4 style='margin: 0.3rem 0; color:#F8FAFC !important;'>{step.title}</h4>
            <div style='font-size:0.85rem; color:#38BDF8;'>Sources: {", ".join([f"<code>{s}</code>" for s in step.source_ids])}</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

        if i < len(chain.links):
            link = chain.links[i]
            lbl = link.label.value
            badge = badge_html("causal", lbl)
            is_explicit = lbl == "explicit_causal_link"
            glow_style = (
                "background: rgba(99, 102, 241, 0.12); border: 1px solid #6366F1; box-shadow: 0 0 15px rgba(99, 102, 241, 0.25); padding: 0.75rem 1.25rem; border-radius: 10px;"
                if is_explicit
                else "background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.08); padding: 0.5rem 1rem; border-radius: 8px;"
            )

            st.markdown(
                f"""
            <div class='dp-chain-link' style='text-align: center; margin: 0.8rem 0;'>
                <div class='dp-chain-arrow'></div>
                <div style='{glow_style} display: inline-block; margin-top: 6px;'>
                    {badge}
                    <div style='color: #E2E8F0; font-size: 0.95rem; margin-top: 4px; font-weight: 500;'>{link.rationale}</div>
                    <div style='color: #94A3B8; font-size: 0.8rem;'>Grounding Evidence: {", ".join([f"<code>{e}</code>" for e in link.evidence_ids])}</div>
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )

    st.markdown("</div>", unsafe_allow_html=True)
