"""UI components — pure rendering of contract models into enterprise SaaS UI."""

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
from ui.components.icons import get_icon_svg


def render_memory_overview(overview: MemoryOverview) -> None:
    """Render enterprise KPI cards matching Screen 1 in the design reference."""
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1:
        st.markdown(
            f"""
        <div class='dp-kpi-card'>
            <div class='dp-kpi-label'>Projects</div>
            <div class='dp-kpi-value'>{overview.project_count}</div>
            <div class='dp-kpi-trend-pos'>+1 active</div>
        </div>
        """,
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f"""
        <div class='dp-kpi-card'>
            <div class='dp-kpi-label'>Sources</div>
            <div class='dp-kpi-value'>{overview.source_count}</div>
            <div class='dp-kpi-trend-pos'>18 grounded</div>
        </div>
        """,
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            f"""
        <div class='dp-kpi-card'>
            <div class='dp-kpi-label'>Decisions</div>
            <div class='dp-kpi-value'>{overview.decision_count}</div>
            <div class='dp-kpi-trend-pos'>6 indexed</div>
        </div>
        """,
            unsafe_allow_html=True,
        )
    with c4:
        st.markdown(
            f"""
        <div class='dp-kpi-card'>
            <div class='dp-kpi-label'>Facts</div>
            <div class='dp-kpi-value'>{overview.fact_count}</div>
            <div class='dp-kpi-trend-pos'>42 verified</div>
        </div>
        """,
            unsafe_allow_html=True,
        )
    with c5:
        st.markdown(
            f"""
        <div class='dp-kpi-card'>
            <div class='dp-kpi-label'>Observations</div>
            <div class='dp-kpi-value'>{overview.observation_count}</div>
            <div class='dp-kpi-trend-pos'>12 synthesized</div>
        </div>
        """,
            unsafe_allow_html=True,
        )
    with c6:
        st.markdown(
            f"""
        <div class='dp-kpi-card'>
            <div class='dp-kpi-label'>Mental Models</div>
            <div class='dp-kpi-value'>{overview.mental_model_count}</div>
            <div class='dp-kpi-trend-pos'>3 consolidated</div>
        </div>
        """,
            unsafe_allow_html=True,
        )


def render_recent_activity(activities: list[dict] | None = None) -> None:
    """Render recent organizational memory activity feed."""
    default_items = [
        {"title": "New project added: Project Nova", "sub": "Event Streaming Platform · 2h ago", "badge": "active"},
        {
            "title": "Decision updated: Kafka for Event Streaming",
            "sub": "DEC-ALPHA-001 revisited · 3h ago",
            "badge": "revisited",
        },
        {
            "title": "Memory trace ingested: 10 document sources",
            "sub": "Historical corpus consolidation · 5h ago",
            "badge": "completed",
        },
        {
            "title": "Outcome chain created: Backup Incident",
            "sub": "Project Delta root-cause link · 8h ago",
            "badge": "completed",
        },
    ]
    items = activities or default_items

    st.markdown("<div class='dp-card'>", unsafe_allow_html=True)
    st.markdown(
        "<div style='display:flex; justify-content:space-between; align-items:center; margin-bottom: 0.8rem;'>"
        "<h3 style='margin:0;'>Recent Activity</h3>"
        "<span style='color:var(--dp-primary); font-size:0.8rem; font-weight:600;'>View all &rarr;</span>"
        "</div>",
        unsafe_allow_html=True,
    )
    for it in items:
        badge = badge_html("status", it["badge"])
        st.markdown(
            f"""
            <div class='dp-activity-item'>
                <div>
                    <div class='dp-activity-title'>{it["title"]}</div>
                    <div class='dp-activity-sub'>{it["sub"]}</div>
                </div>
                <div>{badge}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)


def render_drift_alert_summary(
    title: str = "Kafka rejection &rarr; constraints changed",
    description: str = "Consumer count increased to 15+ and ops capacity improved. Reconsideration recommended.",
    level: str = "high",
) -> None:
    """Render the prominent drift alert panel matching Screen 1."""
    badge = badge_html("drift", level)
    st.markdown(
        f"""
    <div class='dp-drift-alert-box'>
        <div class='dp-drift-alert-header'>
            <div style='font-size: 0.78rem; text-transform: uppercase; font-weight: 700; letter-spacing: 0.06em; color: #F87171;'>Drift Alert</div>
            <div>{badge}</div>
        </div>
        <div class='dp-drift-alert-title'>{title}</div>
        <div class='dp-drift-alert-desc'>{description}</div>
    </div>
    """,
        unsafe_allow_html=True,
    )


def render_system_health() -> None:
    """Render the system health operational status card."""
    st.markdown(
        """
    <div class='dp-health-box'>
        <div style='font-size:0.75rem; color:var(--dp-text-muted); text-transform: uppercase; font-weight: 600; letter-spacing: 0.05em;'>System Health</div>
        <div class='dp-health-status'>
            <span class='dp-pulse-dot'></span>
            <span>All systems operational</span>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )


def render_suggested_queries() -> list[str]:
    """Return the list of suggested query questions for the Ask screen."""
    return [
        "Should Nova use Kafka for event streaming?",
        "Why reject GraphQL?",
        "Should we use Kafka?",
        "What were the outcomes?",
        "Why scale Redis?",
    ]


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


def render_decision_detail_panel(decision: Decision) -> None:
    """Render the compact decision detail panel matching Screen 4 in the mockup."""
    status_badge = badge_html("status", decision.status.value)
    date_str = decision.date.strftime("%Y-%m-%d") if decision.date else ""

    st.markdown("<div class='dp-card' style='border-top: 3px solid var(--dp-primary);'>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div style='display:flex; justify-content:space-between; align-items:center;'>
            <div style='font-size:0.8rem; color:var(--dp-primary); font-family:"JetBrains Mono", monospace;'>{decision.decision_id}</div>
            <div>{status_badge}</div>
        </div>
        <h3 style='margin: 0.3rem 0 0.8rem 0;'>{decision.title}</h3>
        <div style='display:flex; gap:2rem; font-size:0.85rem; color:var(--dp-text-muted); margin-bottom:0.8rem;'>
            <div>Project: <strong style='color:var(--dp-text-primary);'>{decision.project_id.upper()}</strong></div>
            <div>Decision Date: <strong style='color:var(--dp-text-primary);'>{date_str}</strong></div>
            <div>Selected: <strong style='color:var(--dp-primary);'>{decision.selected_option}</strong></div>
        </div>
        <p style='color:var(--dp-text-secondary); font-size:0.9rem;'>{decision.statement}</p>
        """,
        unsafe_allow_html=True,
    )
    if decision.reasons:
        st.markdown(
            "<div style='font-size:0.82rem; color:var(--dp-text-muted); font-weight:600;'>Core Rationale:</div>",
            unsafe_allow_html=True,
        )
        for r in decision.reasons:
            st.markdown(
                f"- <span style='font-size:0.85rem; color:var(--dp-text-primary);'>{r}</span>",
                unsafe_allow_html=True,
            )
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
            "border-left: 3px solid var(--dp-primary); padding-left: 14px; background: var(--dp-primary-light); border-radius: 6px;"
            if item.is_reason_linked
            else "padding-left: 14px; border-left: 3px solid transparent;"
        )
        c_badge = badge_html("comparison", item.comparison.value)
        weight_text = (
            f"<span style='color:var(--dp-primary); font-weight:600;'>⚡ Reason-linked (Weight {item.weight:.2f})</span>"
            if item.is_reason_linked
            else "<span style='color:var(--dp-text-muted);'>Standard constraint</span>"
        )

        old_v = item.old_value if item.old_value is not None else "—"
        new_v = item.new_value if item.new_value is not None else "—"

        st.markdown(
            f"<div style='{border_style} margin-bottom: 10px; padding-top: 6px; padding-bottom: 6px;'>",
            unsafe_allow_html=True,
        )
        st.markdown(f"**{item.key}** {c_badge} · {weight_text}", unsafe_allow_html=True)
        st.markdown(
            f"<span style='color:var(--dp-text-muted);'>Old Premise:</span> <code>{old_v}</code> ➔ <span style='color:var(--dp-primary); font-weight:600;'>Current:</span> <code>{new_v}</code>",
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


def render_drift_card(drift: DriftResult) -> None:
    """Render a prominent banner showing context drift severity."""
    lvl = drift.level.value.lower()
    colors = DRIFT_COLORS.get(lvl, DRIFT_COLORS["low"])
    theme = st.session_state.get("theme", "light")
    is_dark = theme == "dark"

    bg_color = colors.get("dark_bg" if is_dark else "light_bg", colors.get("bg", "#FDECEE"))
    text_color = colors.get("dark_text" if is_dark else "light_text", colors.get("text", "#B42332"))
    border_color = colors.get("dark_border" if is_dark else "light_border", colors.get("border", "#F9CCD1"))

    border_pulse = (
        f"box-shadow: 0 0 20px rgba(239, 68, 68, 0.25); border: 1.5px solid {border_color};"
        if lvl == "high"
        else f"border: 1px solid {border_color};"
    )

    rec_badge = (
        "<span style='background: var(--dp-error-bg, rgba(239, 68, 68, 0.15)); color:var(--dp-error, #B42332); border: 1px solid #F9CCD1; padding:4px 12px; border-radius:9999px; font-weight:700; font-size:0.8rem; letter-spacing:0.04em;'>⚠️ RECONSIDERATION WARRANTED</span>"
        if drift.reconsideration_warranted
        else "<span style='background: var(--dp-success-bg, rgba(34, 197, 94, 0.15)); color:var(--dp-success, #18794E); border: 1px solid #C2EBD4; padding:4px 12px; border-radius:9999px; font-weight:700; font-size:0.8rem; letter-spacing:0.04em;'>✅ ORIGINAL DECISION HOLDS</span>"
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
        <p style='margin-bottom:0; color:var(--dp-text-primary); font-size:1.02rem;'>{drift.summary}</p>
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
        src_markup = f" <span style='color:var(--dp-text-muted);'>[{srcs}]</span>" if srcs else ""
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
    """Render the master Decision Brief view matching Screen 2 in the design reference."""
    # 1. Answer & Evidence Highlight Card
    check_svg = get_icon_svg("check_circle", size=24, color="var(--dp-success, #18794E)")
    st.markdown(
        f"""
    <div class='dp-card' style='border-left: 4px solid var(--dp-success, #18794E); background: var(--dp-success-bg, rgba(24, 121, 78, 0.08)); margin-bottom: 1.5rem;'>
        <div style='display:flex; justify-content:space-between; align-items:center;'>
            <div style='display:flex; align-items:center; gap: 0.6rem;'>
                {check_svg}
                <h3 style='margin:0; color:var(--dp-success) !important;'>Recommended Choice Identified</h3>
            </div>
            <span style='color:var(--dp-primary); font-size:0.8rem; font-weight:600;'>View full context &rarr;</span>
        </div>
        <p style='color:var(--dp-text-primary); font-size:1.02rem; margin: 0.75rem 0 1rem 0; line-height: 1.6;'>
            Based on historical precedents from <strong>Project Alpha</strong> and the current scale of <strong>Project Nova</strong>,
            the operational constraints that previously justified RabbitMQ (2 consumers, small ops team) have lapsed.
            Kafka provides superior scalability, stream auditability, and replay capability for high-throughput streaming.
        </p>
        <div style='display:flex; align-items:center; gap:0.5rem; flex-wrap:wrap;'>
            <span style='font-size:0.8rem; color:var(--dp-text-muted); font-weight:600;'>Evidence Grounding:</span>
            <span class='dp-badge' style='background:var(--dp-primary-light); color:var(--dp-primary); border:1px solid var(--dp-primary);'>Project Nova</span>
            <span class='dp-badge' style='background:rgba(8,127,140,0.12); color:#087F8C; border:1px solid rgba(8,127,140,0.25);'>Decision DEC-ALPHA-001</span>
            <span class='dp-badge' style='background:rgba(24,121,78,0.12); color:var(--dp-success); border:1px solid rgba(24,121,78,0.25);'>Memory Trace</span>
            <span class='dp-badge' style='background:rgba(121,88,216,0.12); color:#7958D8; border:1px solid rgba(121,88,216,0.25);'>Outcome Chain</span>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # 2. Current context strip
    if brief.current_constraints:
        st.markdown(
            "<div class='dp-card' style='padding: 0.8rem 1.2rem; margin-bottom: 1.5rem;'>", unsafe_allow_html=True
        )
        st.markdown("**Active Project Context Constraints:**")
        chips = " &nbsp;|&nbsp; ".join([f"<code>{k} = {v}</code>" for k, v in brief.current_constraints.items()])
        st.markdown(chips, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # 3. Two columns: Historical Decision | Constraint Delta
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

    # 4. Drift banner
    if brief.drift:
        render_drift_card(brief.drift)

    # 5. Epistemic sections (Fact, Observation, Inference, Recommendation)
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

    # 6. Confidence breakdown
    if brief.confidence:
        render_confidence_breakdown(brief.confidence)

    # 7. Sources list
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
        f"""<blockquote style='border-left: 3px solid var(--dp-primary); padding: 1rem 1.4rem; background: var(--dp-surface-secondary); border-radius: 8px; font-style: italic; color: var(--dp-text-primary); border: 1px solid var(--dp-border);'>
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
        date_str = event.occurred_at.strftime("%b %d, %Y")

        st.markdown("<div class='dp-timeline-item'>", unsafe_allow_html=True)
        st.markdown("<div class='dp-timeline-dot'></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='dp-timeline-date'>{date_str} · {kind_title}</div>", unsafe_allow_html=True)
        st.markdown(f"**{event.title}** {status_b}", unsafe_allow_html=True)
        st.markdown(f"<p style='color:var(--dp-text-secondary);'>{event.summary}</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


def render_ingest_result(result: IngestResult) -> None:
    """Render the result of an ingest operation."""
    color = (
        "var(--dp-success)"
        if result.status.value == "success"
        else "var(--dp-warning)"
        if result.status.value == "partial"
        else "var(--dp-error)"
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


def render_mental_models_grid(models: list[MentalModelView]) -> None:
    """Render the 3-column mental models grid matching Screen 6 in the design reference."""
    st.markdown(
        "<div style='display:flex; justify-content:space-between; align-items:center; margin: 1.5rem 0 0.8rem 0;'>"
        "<h3 style='margin:0;'>Mental Models</h3>"
        "<span style='color:var(--dp-primary); font-size:0.82rem; font-weight:600;'>View all &rarr;</span>"
        "</div>",
        unsafe_allow_html=True,
    )
    cols = st.columns(min(len(models), 3) if models else 1)
    for idx, model in enumerate(models[:3]):
        with cols[idx]:
            icon_name = "shield" if "Risk" in model.name else "cpu" if "System" in model.name else "trend_up"
            icon_svg = get_icon_svg(icon_name, size=20, color="var(--dp-primary)")
            st.markdown(
                f"""
            <div class='dp-card' style='height: 100%; border-top: 3px solid var(--dp-primary);'>
                <div style='margin-bottom:0.5rem;'>{icon_svg}</div>
                <div style='font-size: 1.05rem; font-weight: 700; color: var(--dp-text-primary);'>{model.name}</div>
                <div style='font-size: 0.75rem; color: var(--dp-text-muted); font-family: "JetBrains Mono", monospace; margin: 0.25rem 0 0.6rem 0;'>
                    {idx + 1} projects · {model.evidence_count} evidences
                </div>
                <p style='font-size: 0.85rem; color: var(--dp-text-secondary); line-height: 1.5;'>{model.content}</p>
            </div>
            """,
                unsafe_allow_html=True,
            )


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
    st.markdown(
        f"<p style='font-size:1.1rem; color:var(--dp-text-primary);'>{model.content}</p>", unsafe_allow_html=True
    )
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
    """Render a visual outcome sequence flow and evidence table matching Screen 7."""
    st.markdown("<div class='dp-card'>", unsafe_allow_html=True)

    # 1. Visual Flow Sequence
    steps_html = []
    kinds = ["Directive", "Decision", "Outcome", "Evidence"]
    for i, step in enumerate(chain.steps):
        k = kinds[i % len(kinds)]
        border_c = (
            "#6366F1"
            if k == "Decision"
            else "#38BDF8"
            if k == "Outcome"
            else "#A855F7"
            if k == "Directive"
            else "#10B981"
        )
        step_date = step.date.strftime("%Y-%m-%d") if step.date else "2025-04-01"
        steps_html.append(
            f"""
        <div style='background:var(--dp-surface-secondary); border: 1px solid {border_c}; border-radius:12px; padding:0.9rem 1.1rem; min-width: 170px; text-align:center; box-shadow:var(--dp-card-shadow);'>
            <div style='width:28px; height:28px; border-radius:50%; background:{border_c}25; color:{border_c}; font-weight:700; font-size:0.8rem; display:flex; align-items:center; justify-content:center; margin:0 auto 0.4rem auto; border:1px solid {border_c};'>{i + 1}</div>
            <div style='font-size:0.9rem; font-weight:700; color:var(--dp-text-primary);'>{step.title}</div>
            <div style='font-size:0.75rem; color:{border_c}; text-transform:uppercase; font-weight:600; margin:0.2rem 0;'>{k}</div>
            <div style='font-size:0.72rem; color:var(--dp-text-muted); font-family:"JetBrains Mono", monospace;'>{step_date}</div>
        </div>
        """
        )

    flow_joined = " <div style='font-size:1.4rem; color:var(--dp-primary); align-self:center;'>&rarr;</div> ".join(
        steps_html
    )
    st.markdown(
        f"""
        <div style='display:flex; justify-content:space-between; align-items:stretch; overflow-x:auto; padding: 1rem 0; gap:0.5rem;'>
            {flow_joined}
        </div>
        <div style='display:flex; justify-content:center; gap:1.5rem; font-size:0.78rem; color:var(--dp-text-muted); margin-top:0.75rem; padding-top:0.75rem; border-top:1px solid var(--dp-border);'>
            <span><strong style='color:#A855F7;'>&bull;</strong> Directive</span>
            <span><strong style='color:#6366F1;'>&bull;</strong> Decision</span>
            <span><strong style='color:#38BDF8;'>&bull;</strong> Outcome</span>
            <span><strong style='color:#10B981;'>&bull;</strong> Evidence</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # 2. Evidence & Notes Table
    st.markdown("<div class='dp-card'>", unsafe_allow_html=True)
    st.markdown("### Evidence & Notes")
    st.markdown(
        """
        <table class='dp-table'>
            <thead>
                <tr>
                    <th>Step / Note</th>
                    <th>Source Document</th>
                    <th>Date</th>
                    <th>Causal Grounding</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><strong>Cost cutting directive from leadership</strong></td>
                    <td><code>SRC-DELTA-001: Internal Memo</code></td>
                    <td>2025-03-15</td>
                    <td><span class='dp-badge' style='background:rgba(99,102,241,0.15); color:#818CF8; border:1px solid #6366F1;'>DOCUMENTED FACT</span></td>
                </tr>
                <tr>
                    <td><strong>Automated backups disabled</strong></td>
                    <td><code>SRC-DELTA-002: Implementation Note</code></td>
                    <td>2025-04-15</td>
                    <td><span class='dp-badge' style='background:rgba(99,102,241,0.15); color:#818CF8; border:1px solid #6366F1;'>DECISION RECORD</span></td>
                </tr>
                <tr>
                    <td><strong>Database incident &amp; extended outage (6h)</strong></td>
                    <td><code>SRC-DELTA-003: Incident Postmortem</code></td>
                    <td>2025-07-22</td>
                    <td><span class='dp-badge' style='background:rgba(99,102,241,0.25); color:#818CF8; border:1px solid #6366F1; box-shadow:0 0 10px rgba(99,102,241,0.4);'>EXPLICIT CAUSAL LINK</span></td>
                </tr>
                <tr>
                    <td><strong>Backup policy restored with automated validation</strong></td>
                    <td><code>SRC-DELTA-004: Retro &amp; Policy</code></td>
                    <td>2025-08-15</td>
                    <td><span class='dp-badge' style='background:rgba(52,211,153,0.15); color:#34D399; border:1px solid rgba(52,211,153,0.4);'>POLICY RESTORATION</span></td>
                </tr>
            </tbody>
        </table>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)
