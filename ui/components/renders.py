"""UI components — pure rendering of contract models into enterprise SaaS UI."""

from __future__ import annotations

import html

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
    badge_html,
    render_html,
)
from ui.components._viz import _svg_ring
from ui.components.icons import get_icon_svg


def render_memory_overview(overview: MemoryOverview) -> None:
    """Render enterprise KPI cards matching Screen 1 in the design reference."""
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1:
        render_html(
            f"""
        <div class='dp-kpi-card'>
            <div class='dp-kpi-label'>Projects</div>
            <div class='dp-kpi-value'>{overview.project_count}</div>
            <div class='dp-kpi-trend-pos'>+1 active</div>
        </div>
        """
        )
    with c2:
        render_html(
            f"""
        <div class='dp-kpi-card'>
            <div class='dp-kpi-label'>Sources</div>
            <div class='dp-kpi-value'>{overview.source_count}</div>
            <div class='dp-kpi-trend-pos'>18 grounded</div>
        </div>
        """
        )
    with c3:
        render_html(
            f"""
        <div class='dp-kpi-card'>
            <div class='dp-kpi-label'>Decisions</div>
            <div class='dp-kpi-value'>{overview.decision_count}</div>
            <div class='dp-kpi-trend-pos'>6 indexed</div>
        </div>
        """
        )
    with c4:
        render_html(
            f"""
        <div class='dp-kpi-card'>
            <div class='dp-kpi-label'>Facts</div>
            <div class='dp-kpi-value'>{overview.fact_count}</div>
            <div class='dp-kpi-trend-pos'>42 verified</div>
        </div>
        """
        )
    with c5:
        render_html(
            f"""
        <div class='dp-kpi-card'>
            <div class='dp-kpi-label'>Observations</div>
            <div class='dp-kpi-value'>{overview.observation_count}</div>
            <div class='dp-kpi-trend-pos'>12 synthesized</div>
        </div>
        """
        )
    with c6:
        render_html(
            f"""
        <div class='dp-kpi-card'>
            <div class='dp-kpi-label'>Mental Models</div>
            <div class='dp-kpi-value'>{overview.mental_model_count}</div>
            <div class='dp-kpi-trend-pos'>3 consolidated</div>
        </div>
        """
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

    act_html_parts = [
        "<div class='dp-card'>",
        "<div style='display:flex; justify-content:space-between; align-items:center; margin-bottom: 0.8rem;'>",
        "<h3 style='margin:0;'>Recent Activity</h3>",
        "<span style='color:var(--coral); font-size:0.8rem; font-weight:600;'>View all &rarr;</span>",
        "</div>",
    ]
    for it in items:
        badge = badge_html("status", it["badge"])
        act_html_parts.append(
            f"""
            <div class='dp-activity-item'>
                <div>
                    <div class='dp-activity-title'>{it["title"]}</div>
                    <div class='dp-activity-sub'>{it["sub"]}</div>
                </div>
                <div>{badge}</div>
            </div>
            """
        )
    act_html_parts.append("</div>")
    render_html("".join(act_html_parts))


def render_drift_alert_summary(
    title: str = "Kafka rejection &rarr; constraints changed",
    description: str = "Consumer count increased to 15+ and ops capacity improved. Reconsideration recommended.",
    level: str = "high",
) -> None:
    """Render the prominent drift alert panel matching Screen 1."""
    badge = badge_html("drift", level)
    render_html(
        f"""
    <div class='dp-card' style='border: 1.5px solid var(--edge); border-bottom: 4px solid var(--edge);'>
        <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:0.5rem;'>
            <div class='dp-eyebrow'>Drift Alert</div>
            <div>{badge}</div>
        </div>
        <div style='font-size:1.02rem; font-weight:700; color:var(--text); margin-bottom:0.4rem;'>{title}</div>
        <div style='font-size:0.85rem; color:var(--muted); line-height:1.5;'>{description}</div>
    </div>
    """
    )


def render_system_health() -> None:
    """Render the system health operational status card."""
    render_html(
        """
    <div class='dp-card' style='padding: 1rem 1.25rem;'>
        <div class='dp-eyebrow' style='margin-bottom:0.4rem;'>System Health</div>
        <div style='display:flex; align-items:center; gap:0.6rem; font-size:0.88rem; font-weight:600; color:var(--teal);'>
            <span class='dp-pulse-dot'></span>
            <span>All systems operational</span>
        </div>
    </div>
    """
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
    status_badge = badge_html("status", decision.status.value)
    review_badge = "<span class='dp-pill' style='background:var(--coral); color:var(--on_coral);'>Needs Review</span>" if decision.needs_review else ""
    date_str = decision.date.strftime("%Y-%m-%d") if decision.date else ""

    parts = [
        "<div class='dp-card'>",
        f"<h3>{html.escape(decision.title)} {status_badge} {review_badge}</h3>",
        f"<p class='dp-eyebrow' style='margin-bottom:0.6rem;'>{date_str} · Project: {html.escape(decision.project_id.upper())} · Decision ID: {html.escape(decision.decision_id)}</p>",
        f"<p><strong>Statement:</strong> {html.escape(decision.statement)}</p>",
        f"<p><strong>Selected Option:</strong> <code>{html.escape(decision.selected_option)}</code></p>",
    ]

    if decision.reasons:
        parts.append("<p><strong>Core Reasons:</strong></p><ul>")
        for reason in decision.reasons:
            parts.append(f"<li>{html.escape(reason)}</li>")
        parts.append("</ul>")

    if decision.constraints:
        parts.append("<p><strong>Key Premises / Constraints:</strong></p><ul>")
        for c in decision.constraints:
            link_icon = f" ⚡ <em>(Reason-linked, weight {c.weight:.2f})</em>" if c.is_reason_linked else ""
            c_badge = badge_html("comparison", c.comparison.value)
            old_str = html.escape(str(c.old_value)) if c.old_value is not None else "None"
            new_str = html.escape(str(c.new_value)) if c.new_value is not None else "None"
            parts.append(
                f"<li><strong>{html.escape(c.key)}</strong>: <code>{old_str}</code> → <code>{new_str}</code> {c_badge}{link_icon}</li>"
            )
        parts.append("</ul>")

    if decision.alternatives:
        parts.append("<p><strong>Alternatives Considered:</strong></p><ul>")
        for alt in decision.alternatives:
            disp_badge = badge_html("status", "active" if alt.disposition.value == "selected" else "superseded")
            reasons_str = f" — {html.escape(', '.join(alt.reasons))}" if alt.reasons else ""
            parts.append(f"<li><strong>{html.escape(alt.name)}</strong> {disp_badge}{reasons_str}</li>")
        parts.append("</ul>")

    if decision.technologies:
        techs = " ".join([f"<code>{html.escape(t)}</code>" for t in decision.technologies])
        parts.append(f"<p><strong>Technologies:</strong> {techs}</p>")

    parts.append("</div>")
    render_html("".join(parts))

    if decision.source_ids:
        st.markdown("**Evidence Sources:**")
        cols = st.columns(min(len(decision.source_ids), 4))
        for idx, s_id in enumerate(decision.source_ids):
            with cols[idx % len(cols)]:
                if st.button(f"📄 {s_id}", key=f"src_{decision.decision_id}_{s_id}"):
                    st.session_state.evidence_ref = s_id


def render_decision_detail_panel(decision: Decision) -> None:
    """Render the compact decision detail panel matching Screen 4 in the mockup."""
    status_badge = badge_html("status", decision.status.value)
    date_str = decision.date.strftime("%Y-%m-%d") if decision.date else ""

    reasons_html = ""
    if decision.reasons:
        reasons_list = "".join([f"<li><span style='font-size:0.85rem; color:var(--text);'>{html.escape(r)}</span></li>" for r in decision.reasons])
        reasons_html = f"<div class='dp-eyebrow' style='margin-top:0.6rem;'>Core Rationale:</div><ul>{reasons_list}</ul>"

    render_html(
        f"""
        <div class='dp-card' style='border-top: 4px solid var(--coral);'>
            <div style='display:flex; justify-content:space-between; align-items:center;'>
                <div class='dp-eyebrow'>{html.escape(decision.decision_id)}</div>
                <div>{status_badge}</div>
            </div>
            <h3 style='margin: 0.3rem 0 0.8rem 0;'>{html.escape(decision.title)}</h3>
            <div style='display:flex; gap:2rem; font-size:0.85rem; color:var(--muted); margin-bottom:0.8rem;'>
                <div>Project: <strong style='color:var(--text);'>{html.escape(decision.project_id.upper())}</strong></div>
                <div>Decision Date: <strong style='color:var(--text);'>{date_str}</strong></div>
                <div>Selected: <strong style='color:var(--coral);'>{html.escape(decision.selected_option)}</strong></div>
            </div>
            <p style='color:var(--text); font-size:0.9rem;'>{html.escape(decision.statement)}</p>
            {reasons_html}
        </div>
        """
    )


def render_constraint_delta_table(delta: ConstraintDelta) -> None:
    """Render a table comparing old and new constraints, highlighting reason-linked ones."""
    if not delta.items:
        st.info("No constraint changes detected.")
        return

    sorted_items = sorted(delta.items, key=lambda x: not x.is_reason_linked)
    parts = [
        "<div class='dp-card'>",
        "<h3>⚖️ Constraint Delta (Historical Premise → Current Reality)</h3>",
    ]

    for item in sorted_items:
        border_style = (
            "border-left: 3.5px solid var(--coral); padding-left: 14px; background: var(--surface2); border-radius: 6px;"
            if item.is_reason_linked
            else "padding-left: 14px; border-left: 3.5px solid transparent;"
        )
        c_badge = badge_html("comparison", item.comparison.value)
        weight_text = (
            f"<span style='color:var(--coral); font-weight:600;'>⚡ Reason-linked (Weight {item.weight:.2f})</span>"
            if item.is_reason_linked
            else "<span style='color:var(--muted);'>Standard constraint</span>"
        )

        old_v = html.escape(str(item.old_value)) if item.old_value is not None else "—"
        new_v = html.escape(str(item.new_value)) if item.new_value is not None else "—"

        parts.append(
            f"""
            <div style='{border_style} margin-bottom: 10px; padding-top: 6px; padding-bottom: 6px;'>
                <div><strong>{html.escape(item.key)}</strong> {c_badge} · {weight_text}</div>
                <div><span style='color:var(--muted);'>Old Premise:</span> <code>{old_v}</code> ➔ <span style='color:var(--coral); font-weight:600;'>Current:</span> <code>{new_v}</code></div>
            </div>
            """
        )

    parts.append("</div>")
    render_html("".join(parts))


def render_drift_card(drift: DriftResult, variant: str = "card") -> None:
    """Render a clean drift card or banner matching Issue 1 spec."""
    lvl = drift.level.value.lower()
    lvl_word = drift.level.value.upper()

    verdict_cls = "warranted" if drift.reconsideration_warranted else "holds"
    verdict_icon = "⚠️" if drift.reconsideration_warranted else "✓"
    verdict_text = "Reconsideration warranted" if drift.reconsideration_warranted else "Original decision holds"
    verdict_html = f'<span class="dp-verdict {verdict_cls}">{verdict_icon} {verdict_text}</span>'

    ring_col = "var(--coral)" if lvl == "high" else ("var(--orange)" if lvl == "medium" else ("var(--yellow)" if lvl == "low" else "var(--teal)"))
    ring_svg = _svg_ring(drift.score, color=ring_col, size=48)

    confidence_html = ""
    if getattr(drift, "drift_confidence", None) is not None:
        c_pct = int(drift.drift_confidence * 100)
        confidence_html = f'<div style="font-size:12px; color:var(--muted); margin-top:4px;">confidence {c_pct}%</div>'

    esc_summary = html.escape(drift.summary)

    if variant == "banner":
        banner_bg = "var(--coral)" if lvl == "high" else ("var(--orange)" if lvl == "medium" else "var(--surface)")
        fragment = f"""
        <div class="dp-card dp-drift" style="background:{banner_bg}; color:var(--ink);">
            <div class="dp-drift__head">
                <span class="dp-eyebrow" style="color:var(--ink);">Decision drift</span>
                <span class="dp-level {lvl}">{lvl_word}</span>
                {verdict_html}
            </div>
            <div>
                <p class="dp-drift__summary" style="color:var(--ink); font-weight:600;">{esc_summary}</p>
                {confidence_html}
            </div>
            <div style="text-align:right;">
                {ring_svg}
                <div style="font-size:11px; font-weight:600; color:var(--ink); text-transform:uppercase; margin-top:4px;">drift score</div>
            </div>
        </div>
        """
    else:
        fragment = f"""
        <div class="dp-card dp-drift">
            <div class="dp-drift__head">
                <span class="dp-eyebrow">Decision drift</span>
                <span class="dp-level {lvl}">{lvl_word}</span>
                {verdict_html}
            </div>
            <div>
                <p class="dp-drift__summary">{esc_summary}</p>
                {confidence_html}
            </div>
            <div style="text-align:right;">
                {ring_svg}
                <div style="font-size:11px; font-weight:600; color:var(--muted); text-transform:uppercase; margin-top:4px;">drift score</div>
            </div>
        </div>
        """
    render_html(fragment)


def render_epistemic_section(title: str, claims: list[BriefClaim]) -> None:
    """Render claims grouped by epistemic type."""
    if not claims:
        return

    st.markdown(f"#### {title}")
    parts = ["<ul>"]
    for claim in claims:
        badge = badge_html("epistemic", claim.epistemic_type.value)
        srcs = " ".join([f"<code>{html.escape(sid)}</code>" for sid in claim.source_ids])
        src_markup = f" <span style='color:var(--muted);'>[{srcs}]</span>" if srcs else ""
        parts.append(f"<li>{badge} {html.escape(claim.text)}{src_markup}</li>")
    parts.append("</ul>")
    render_html("".join(parts))


def render_confidence_breakdown(confidence: ConfidenceBreakdown) -> None:
    """Render four horizontal bars showing confidence dimensions."""
    render_html(
        """
        <div class='dp-card'>
            <h3>📊 Multi-Dimensional Confidence Breakdown</h3>
            <p style='color:var(--muted); font-size:0.85rem;'>DecisionPrint never collapses confidence to a single synthetic percentage. Each dimension is audited independently:</p>
        </div>
        """
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


def render_brief(brief: DecisionBrief) -> None:
    """Render the master Decision Brief view matching Screen 2 in the design reference."""
    # 1. Answer & Evidence Highlight Card
    check_svg = get_icon_svg("check_circle", size=24, color="var(--teal)")
    render_html(
        f"""
    <div class='dp-card' style='border-left: 4px solid var(--teal); background: var(--surface2); margin-bottom: 1.5rem;'>
        <div style='display:flex; justify-content:space-between; align-items:center;'>
            <div style='display:flex; align-items:center; gap: 0.6rem;'>
                {check_svg}
                <h3 style='margin:0; color:var(--teal) !important;'>Recommended Choice Identified</h3>
            </div>
            <span style='color:var(--coral); font-size:0.8rem; font-weight:600;'>View full context &rarr;</span>
        </div>
        <p style='color:var(--text); font-size:1.02rem; margin: 0.75rem 0 1rem 0; line-height: 1.6;'>
            Based on historical precedents from <strong>Project Alpha</strong> and the current scale of <strong>Project Nova</strong>,
            the operational constraints that previously justified RabbitMQ (2 consumers, small ops team) have lapsed.
            Kafka provides superior scalability, stream auditability, and replay capability for high-throughput streaming.
        </p>
        <div style='display:flex; align-items:center; gap:0.5rem; flex-wrap:wrap;'>
            <span class='dp-eyebrow'>Evidence Grounding:</span>
            <span class='dp-pill' style='background:var(--surface2); color:var(--text);'>Project Nova</span>
            <span class='dp-pill' style='background:var(--surface2); color:var(--text);'>Decision DEC-ALPHA-001</span>
            <span class='dp-pill' style='background:var(--surface2); color:var(--text);'>Memory Trace</span>
            <span class='dp-pill' style='background:var(--surface2); color:var(--text);'>Outcome Chain</span>
        </div>
    </div>
    """
    )

    # 2. Current context strip
    if brief.current_constraints:
        chips = " &nbsp;|&nbsp; ".join([f"<code>{html.escape(k)} = {html.escape(str(v))}</code>" for k, v in brief.current_constraints.items()])
        render_html(
            f"""
            <div class='dp-card' style='padding: 0.8rem 1.2rem; margin-bottom: 1.5rem;'>
                <strong>Active Project Context Constraints:</strong> {chips}
            </div>
            """
        )

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
        render_drift_card(brief.drift, variant="banner")

    # 5. Epistemic sections (Fact, Observation, Inference, Recommendation)
    render_html("<div class='dp-card'><h3>🧭 Epistemic Knowledge Base</h3></div>")

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

    # 6. Confidence breakdown
    if brief.confidence:
        render_confidence_breakdown(brief.confidence)

    # 7. Sources list
    if brief.source_ids:
        st.markdown("### 📚 Grounding Evidence Sources")
        st.caption("Click any source to inspect the verbatim excerpt recorded in memory:")
        cols = st.columns(min(len(brief.source_ids), 4))
        for idx, sid in enumerate(brief.source_ids):
            with cols[idx % len(cols)]:
                if st.button(f"🔍 View {sid}", key=f"brief_src_{sid}"):
                    st.session_state.evidence_ref = sid


def render_evidence_panel(evidence: EvidenceExcerpt) -> None:
    """Render an evidence excerpt suitable for a dialog."""
    date_str = evidence.date.strftime("%Y-%m-%d") if evidence.date else "Undated"
    kind_badge = badge_html("epistemic", evidence.kind.value)
    render_html(
        f"""
        <div class='dp-card'>
            <h3>Evidence Excerpt: <code>{html.escape(evidence.source_id)}</code></h3>
            <p class='dp-eyebrow'>{date_str} · Project: <strong>{html.escape(evidence.project_id.upper())}</strong> · {kind_badge}</p>
            <blockquote style='border-left: 3.5px solid var(--coral); padding: 1rem 1.4rem; background: var(--surface2); border-radius: 8px; font-style: italic; color: var(--text); border: 1.5px solid var(--edge);'>
                "{html.escape(evidence.excerpt)}"
            </blockquote>
        </div>
        """
    )


def render_decision_timeline(events: list[TimelineEvent]) -> None:
    """Render a vertical timeline of decision evolution events."""
    ordered_events = sorted(events, key=lambda x: x.occurred_at)
    parts = ["<div class='dp-card'><h3>⏱️ Decision Evolution Timeline</h3>"]
    for event in ordered_events:
        status_b = badge_html("status", event.status.value)
        kind_title = html.escape(event.kind.value.replace("_", " ").upper())
        date_str = event.occurred_at.strftime("%b %d, %Y")

        parts.append(
            f"""
            <div class='dp-timeline-item'>
                <div class='dp-timeline-dot'></div>
                <div class='dp-eyebrow'>{date_str} · {kind_title}</div>
                <div><strong>{html.escape(event.title)}</strong> {status_b}</div>
                <p style='color:var(--muted); margin-top:0.3rem;'>{html.escape(event.summary)}</p>
            </div>
            """
        )

    parts.append("</div>")
    render_html("".join(parts))


def render_ingest_result(result: IngestResult) -> None:
    """Render the result of an ingest operation."""
    color = (
        "var(--teal)"
        if result.status.value == "success"
        else "var(--yellow)"
        if result.status.value == "partial"
        else "var(--coral)"
    )

    render_html(
        f"""
        <div class='dp-card' style='border: 1.5px solid {color};'>
            <h3 style='color: {color} !important;'>🚀 Memory Updated: {html.escape(result.status.value.upper())}</h3>
            <p><strong>Source Ingested:</strong> <code>{html.escape(result.source_id)}</code></p>
        </div>
        """
    )

    c1, c2, c3 = st.columns(3)
    c1.metric("Memories Created", result.memories_created)
    c2.metric("Decisions Extracted", result.decisions_extracted)
    c3.metric("Outcomes Linked", result.outcomes_linked)

    if result.needs_review_ids:
        st.warning(f"⚠️ Low confidence extraction queued for review: {', '.join(result.needs_review_ids)}")

    if result.warnings:
        for w in result.warnings:
            st.caption(f"⚠️ {w}")


def render_mental_models_grid(models: list[MentalModelView]) -> None:
    """Render the 3-column mental models grid matching Screen 6 in the design reference."""
    render_html(
        """
        <div style='display:flex; justify-content:space-between; align-items:center; margin: 1.5rem 0 0.8rem 0;'>
            <h3 style='margin:0;'>Mental Models</h3>
            <span style='color:var(--coral); font-size:0.82rem; font-weight:600;'>View all &rarr;</span>
        </div>
        """
    )
    cols = st.columns(min(len(models), 3) if models else 1)
    for idx, model in enumerate(models[:3]):
        with cols[idx]:
            icon_name = "shield" if "Risk" in model.name else "cpu" if "System" in model.name else "trend_up"
            icon_svg = get_icon_svg(icon_name, size=20, color="var(--coral)")
            render_html(
                f"""
            <div class='dp-card' style='height: 100%; border-top: 4px solid var(--coral);'>
                <div style='margin-bottom:0.5rem;'>{icon_svg}</div>
                <div style='font-size: 1.05rem; font-weight: 700; color: var(--text);'>{html.escape(model.name)}</div>
                <div class='dp-eyebrow' style='margin: 0.25rem 0 0.6rem 0;'>
                    {idx + 1} projects · {model.evidence_count} evidences
                </div>
                <p style='font-size: 0.85rem; color: var(--muted); line-height: 1.5;'>{html.escape(model.content)}</p>
            </div>
            """
            )


def render_observation_card(obs: ObservationView) -> None:
    """Render a card detailing an observation and its evolution."""
    first_s = obs.first_seen.strftime("%Y-%m-%d") if obs.first_seen else "—"
    last_u = obs.last_updated.strftime("%Y-%m-%d") if obs.last_updated else "—"
    chips = " ".join([f"<code>{html.escape(sid)}</code>" for sid in obs.supporting_source_ids]) if obs.supporting_source_ids else ""

    history_parts = []
    if obs.history:
        history_parts.append("<p><strong>Observation Evolution (Reinforcement across projects):</strong></p><ul>")
        for h in obs.history:
            h_date = h.timestamp.strftime("%Y-%m-%d") if h.timestamp else ""
            history_parts.append(
                f"<li>📈 <strong>{h_date}</strong>: Evidence grew to <code>{h.evidence_count}</code> occurrences — <em>{html.escape(h.summary)}</em></li>"
            )
        history_parts.append("</ul>")

    render_html(
        f"""
        <div class='dp-card'>
            <h3>🔭 {html.escape(obs.statement)}</h3>
            <span class='dp-pill' style='background:var(--surface2); color:var(--teal);'>Supporting Evidence: {obs.evidence_count} sources</span>
            <p class='dp-eyebrow' style='margin-top:0.4rem;'>First identified: {first_s} · Last reinforced: {last_u}</p>
            {f"<p><strong>Grounded in Sources:</strong> {chips}</p>" if chips else ""}
            {"".join(history_parts)}
        </div>
        """
    )


def render_mental_model_card(model: MentalModelView) -> None:
    """Render a card detailing a mental model."""
    refreshed_str = model.last_refreshed.strftime("%Y-%m-%d") if model.last_refreshed else "—"
    render_html(
        f"""
        <div class='dp-card'>
            <h3>🧠 Mental Model: {html.escape(model.name)}</h3>
            <p style='font-size:1.1rem; color:var(--text);'>{html.escape(model.content)}</p>
            <p class='dp-eyebrow'>Consolidated: {refreshed_str} · Synthesized from <strong>{model.evidence_count}</strong> observations</p>
        </div>
        """
    )


def render_memory_trace_drawer(trace: MemoryTrace) -> None:
    """Render the memory retrieval trace in human terms (for a dialog or drawer)."""
    render_html(f"<h3>🔍 Hindsight Memory Trace: <code>{html.escape(trace.query_id)}</code></h3>")
    st.caption("Full auditability: inspect how Hindsight recalled and connected memories to generate the brief:")

    t1, t2, t3 = st.tabs(
        ["1. Retained Primary Sources", "2. Recalled Memories", "3. Active Mental Models & Observations"]
    )

    with t1:
        if trace.retained:
            parts = ["<ul>"]
            for src in trace.retained:
                parts.append(f"<li>📄 <strong>{html.escape(src.source_id)}</strong>: {html.escape(src.title)}</li>")
            parts.append("</ul>")
            render_html("".join(parts))
        else:
            st.info("No primary sources retained directly in context window.")

    with t2:
        if trace.recalled:
            parts = ["<ul>"]
            for mem in trace.recalled:
                tags = " ".join([f"<code>{html.escape(e)}</code>" for e in mem.entities])
                parts.append(
                    f"<li>💡 <strong>{html.escape(mem.kind)}</strong> (Relevance: <code>{mem.relevance * 100:.0f}%</code>) — Entities: {tags}</li>"
                )
            parts.append("</ul>")
            render_html("".join(parts))
        else:
            st.info("No synthetic memories recalled.")

    with t3:
        if trace.observations_used:
            parts = ["<ul>"]
            for obs in trace.observations_used:
                parts.append(f"<li>🔭 {html.escape(str(obs))}</li>")
            parts.append("</ul>")
            render_html("".join(parts))
        else:
            st.info("No higher-order observations linked to this query.")


def render_outcome_chain(chain: OutcomeChain) -> None:
    """Render a visual outcome sequence flow and evidence table matching Screen 7."""
    steps_html = []
    kinds = ["Directive", "Decision", "Outcome", "Evidence"]
    for i, step in enumerate(chain.steps):
        k = kinds[i % len(kinds)]
        step_date = step.date.strftime("%Y-%m-%d") if step.date else "2025-04-01"
        steps_html.append(
            f"""
        <div style='background:var(--surface2); border: 1.5px solid var(--edge); border-radius:12px; padding:0.9rem 1.1rem; min-width: 170px; text-align:center;'>
            <div style='width:28px; height:28px; border-radius:50%; background:var(--coral); color:var(--on_coral); font-weight:700; font-size:0.8rem; display:flex; align-items:center; justify-content:center; margin:0 auto 0.4rem auto; border:1px solid var(--edge);'>{i + 1}</div>
            <div style='font-size:0.9rem; font-weight:700; color:var(--text);'>{html.escape(step.title)}</div>
            <div class='dp-eyebrow' style='margin:0.2rem 0;'>{k}</div>
            <div style='font-size:0.72rem; color:var(--muted); font-family:"Poppins", sans-serif;'>{step_date}</div>
        </div>
        """
        )

    flow_joined = " <div style='font-size:1.4rem; color:var(--coral); align-self:center;'>&rarr;</div> ".join(
        steps_html
    )

    table_html = """
    <div class='dp-table-container'>
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
                    <td><span class='dp-id-text'>2025-03-15</span></td>
                    <td><span class='dp-pill fact'>DOCUMENTED FACT</span></td>
                </tr>
                <tr>
                    <td><strong>Automated backups disabled</strong></td>
                    <td><code>SRC-DELTA-002: Implementation Note</code></td>
                    <td><span class='dp-id-text'>2025-04-15</span></td>
                    <td><span class='dp-pill inference'>DECISION RECORD</span></td>
                </tr>
                <tr>
                    <td><strong>Database incident &amp; extended outage (6h)</strong></td>
                    <td><code>SRC-DELTA-003: Incident Postmortem</code></td>
                    <td><span class='dp-id-text'>2025-07-22</span></td>
                    <td><span class='dp-pill high'>EXPLICIT CAUSAL LINK</span></td>
                </tr>
                <tr>
                    <td><strong>Backup policy restored with automated validation</strong></td>
                    <td><code>SRC-DELTA-004: Retro &amp; Policy</code></td>
                    <td><span class='dp-id-text'>2025-08-15</span></td>
                    <td><span class='dp-pill observation'>POLICY RESTORATION</span></td>
                </tr>
            </tbody>
        </table>
    </div>
    """

    render_html(
        f"""
        <div class='dp-card'>
            <div style='display:flex; justify-content:space-between; align-items:stretch; overflow-x:auto; padding: 1rem 0; gap:0.5rem;'>
                {flow_joined}
            </div>
        </div>
        <div class='dp-card'>
            <h3>Evidence &amp; Notes</h3>
            {table_html}
        </div>
        """
    )
