"""
DecisionPrint — Dynamic Streamlit UI.

Everything rendered here is data-driven:
  - The sidebar and all metrics come from the backend.
  - Projects, decisions, drift, evidence, and timeline are loaded at runtime.
  - The ingest panel writes real markdown files on upload.
  - Constraint comparison and drift are computed dynamically.
  - No static labels, no hardcoded project names, no dummy fixtures.
"""

from __future__ import annotations

import streamlit as st
import pandas as pd
from datetime import UTC, datetime

from ui.adapters import get_backend
from contracts import (
    Comparison,
    Constraint,
    ConstraintDeltaItem,
    DecisionFilter,
    SourceManifestEntry,
    SourceType,
)
from contracts.errors import NotFoundError

# ── page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="DecisionPrint",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── custom CSS ─────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* ── global ── */
    html, body, [class*="css"] {font-family: 'Inter', sans-serif;}
    .main .block-container {padding-top: 1.5rem; padding-bottom: 2rem;}

    /* ── metric cards ── */
    div[data-testid="metric-container"] {
        background: linear-gradient(135deg,#1a1c2c 0%,#24294a 100%);
        border: 1px solid #3d4168;
        border-radius: 12px;
        padding: 1rem 1.2rem;
        color: white !important;
    }
    div[data-testid="metric-container"] label {color: #a0a8d0 !important; font-size:0.78rem;}
    div[data-testid="metric-container"] [data-testid="metric-value"] {color: #c7d2fe !important; font-size:2rem; font-weight:700;}

    /* ── decision cards ── */
    .dec-card {
        border-left: 4px solid #6366f1;
        background: #1e2139;
        border-radius: 8px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.9rem;
        color: #e2e8f0;
    }
    .dec-card h4 {color: #a5b4fc; margin: 0 0 .4rem 0; font-size:1.05rem;}
    .dec-card .meta {color: #64748b; font-size: 0.78rem; margin-bottom: 0.5rem;}
    .dec-card .statement {color: #cbd5e1; font-size: 0.9rem;}

    /* ── drift badges ── */
    .badge-high {background:#7f1d1d; color:#fca5a5; border-radius:4px; padding:2px 8px; font-size:.75rem; font-weight:600;}
    .badge-medium {background:#78350f; color:#fcd34d; border-radius:4px; padding:2px 8px; font-size:.75rem; font-weight:600;}
    .badge-low {background:#14532d; color:#86efac; border-radius:4px; padding:2px 8px; font-size:.75rem; font-weight:600;}
    .badge-none {background:#1e293b; color:#94a3b8; border-radius:4px; padding:2px 8px; font-size:.75rem; font-weight:600;}

    /* ── constraint delta table ── */
    .delta-changed {color: #fca5a5; font-weight: 600;}
    .delta-same {color: #86efac;}
    .delta-unknown {color: #94a3b8; font-style: italic;}
    .delta-new {color: #93c5fd;}

    /* ── sidebar ── */
    section[data-testid="stSidebar"] {background: #0f1021;}
    section[data-testid="stSidebar"] * {color: #c7d2fe;}

    /* ── tabs ── */
    button[data-baseweb="tab"] {color: #94a3b8 !important;}
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #a5b4fc !important;
        border-bottom: 2px solid #6366f1 !important;
    }

    /* ── causal chain ── */
    .chain-step {
        background: #1e2139;
        border-radius: 8px;
        padding: .7rem 1rem;
        margin-bottom: .5rem;
        border-left: 3px solid #6366f1;
    }
    .chain-link {
        text-align: center;
        color: #64748b;
        font-size: .8rem;
        padding: .2rem 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── backend ─────────────────────────────────────────────────────────────────────
@st.cache_resource
def _backend():
    return get_backend()

def _fresh_backend():
    """Force a fresh backend instance (used after ingest)."""
    _backend.clear()
    return _backend()

# ── helpers ─────────────────────────────────────────────────────────────────────
DRIFT_BADGE = {
    "high":   '<span class="badge-high">HIGH</span>',
    "medium": '<span class="badge-medium">MEDIUM</span>',
    "low":    '<span class="badge-low">LOW</span>',
    "none":   '<span class="badge-none">NONE</span>',
}

def drift_badge(level: str) -> str:
    return DRIFT_BADGE.get(str(level).lower(), f"<span>{level}</span>")

def confidence_bar(value: float | None, label: str) -> None:
    if value is None:
        return
    pct = int(value * 100)
    color = "#22c55e" if pct >= 70 else ("#f59e0b" if pct >= 40 else "#ef4444")
    st.markdown(
        f"""
        <div style="margin-bottom:.4rem;">
          <span style="color:#94a3b8;font-size:.78rem;">{label}</span>
          <div style="background:#1e2139;border-radius:4px;height:8px;margin-top:3px;">
            <div style="background:{color};width:{pct}%;height:8px;border-radius:4px;"></div>
          </div>
          <span style="color:{color};font-size:.72rem;">{pct}%</span>
        </div>""",
        unsafe_allow_html=True,
    )


def render_constraint_delta(items: list[ConstraintDeltaItem]) -> None:
    """Render a visual constraint delta comparison table."""
    if not items:
        return

    st.markdown("#### ⚖️ Constraint Comparison")
    rows = []
    for item in items:
        comp = item.comparison
        if isinstance(comp, Comparison):
            comp_val = comp.value
        else:
            comp_val = str(comp)

        icon = {
            "changed": "🔴",
            "same": "🟢",
            "unknown": "⚪",
            "newly_present": "🔵",
            "incomparable": "🟡",
        }.get(comp_val, "⚪")

        rows.append({
            "": icon,
            "Constraint": item.key,
            "Historical": str(item.old_value or item.historical_value or "—"),
            "Current": str(item.new_value or item.current_value or "—"),
            "Status": comp_val.upper(),
            "Reason-linked": "✓" if item.is_reason_linked else "",
        })

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)


# ── sidebar ──────────────────────────────────────────────────────────────────────
def render_sidebar(backend) -> tuple[str, str]:
    with st.sidebar:
        st.markdown("## 🧠 DecisionPrint")
        st.caption("Living Organizational Decision Memory")
        st.divider()

        role = st.selectbox("Role", ["admin", "engineer", "project_lead", "executive"], key="role")

        overview = backend.get_memory_overview(role)
        projects = backend.list_projects(role)

        project_ids = [p.project_id for p in projects]
        project_id = st.selectbox(
            "Active Project",
            options=project_ids if project_ids else ["—"],
            key="project_id",
        )

        st.divider()
        st.markdown("### 📊 Memory Stats")
        for label, val in [
            ("Projects", overview.project_count),
            ("Decisions", overview.decision_count),
            ("Sources", overview.source_count),
            ("Facts", overview.fact_count),
            ("Observations", overview.observation_count),
            ("Mental Models", overview.mental_model_count),
        ]:
            st.markdown(
                f"<div style='display:flex;justify-content:space-between;color:#94a3b8;font-size:.85rem;'>"
                f"<span>{label}</span><span style='color:#a5b4fc;font-weight:600;'>{val}</span></div>",
                unsafe_allow_html=True,
            )

        if overview.last_updated:
            st.caption(f"Last updated: {overview.last_updated.strftime('%Y-%m-%d %H:%M')}")

    return role, project_id


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE RENDERERS
# ═══════════════════════════════════════════════════════════════════════════════

def render_overview(backend, role: str, project_id: str) -> None:
    overview = backend.get_memory_overview(role)

    st.markdown("## 🧠 Organizational Memory Overview")
    st.markdown(
        f"*Memory learned from **{overview.project_count}** projects · "
        f"**{overview.decision_count}** decisions · "
        f"**{overview.source_count}** sources · "
        f"**{overview.observation_count}** observations*"
    )

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    for col, (label, val) in zip(
        [c1, c2, c3, c4, c5, c6],
        [
            ("Projects", overview.project_count),
            ("Decisions", overview.decision_count),
            ("Sources", overview.source_count),
            ("Facts", overview.fact_count),
            ("Observations", overview.observation_count),
            ("Mental Models", overview.mental_model_count),
        ],
    ):
        col.metric(label, val)

    st.divider()

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("### 📁 Projects")
        projects = backend.list_projects(role)
        if not projects:
            st.info("No projects loaded yet. Upload a file to get started.")
        else:
            rows = []
            for p in projects:
                constraint_count = 0
                if isinstance(p.constraints, list):
                    constraint_count = len(p.constraints)
                elif isinstance(p.constraints, dict):
                    constraint_count = len(p.constraints)
                rows.append({
                    "Project ID": p.project_id,
                    "Name": p.project_name or p.project_id,
                    "Constraints": constraint_count,
                    "Updated": p.updated_at.strftime("%Y-%m-%d") if p.updated_at else "—",
                })
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    with col_b:
        st.markdown("### 🧠 Mental Models")
        models = backend.list_mental_models(role)
        if not models:
            st.info("No mental models found.")
        else:
            for m in models:
                with st.expander(m.name):
                    st.write(m.content)
                    st.caption(f"Evidence count: {m.evidence_count}")


def render_decisions(backend, role: str, project_id: str) -> None:
    st.markdown("## 🧠 Decision Explorer")

    # ── filters ──
    f_col1, f_col2, f_col3, f_col4 = st.columns(4)
    with f_col1:
        text_q = st.text_input("Search text", placeholder="e.g. kafka, redis, backup…")
    with f_col2:
        projects = backend.list_projects(role)
        proj_options = ["(all)"] + [p.project_id for p in projects]
        proj_filter = st.selectbox("Filter by project", proj_options)
    with f_col3:
        tech_q = st.text_input("Technology", placeholder="e.g. kafka, graphql…")
    with f_col4:
        status_options = ["(all)", "active", "reconsidered", "superseded", "exception"]
        status_filter = st.selectbox("Status", status_options)

    from contracts.enums import DecisionStatus
    dec_filter = DecisionFilter(
        text=text_q or None,
        project_id=None if proj_filter == "(all)" else proj_filter,
        technology=tech_q or None,
        status=None if status_filter == "(all)" else DecisionStatus(status_filter),
    )

    decisions = backend.search_decisions(dec_filter, role)

    if not decisions:
        st.warning("No decisions match your filters.")
        return

    st.markdown(f"**{len(decisions)} decision(s) found**")

    for d in decisions:
        did = d.decision_id or d.title
        with st.container():
            st.markdown(
                f"""
                <div class="dec-card">
                  <h4>{d.title}</h4>
                  <div class="meta">
                    📅 {d.date.strftime('%Y-%m-%d') if d.date else '—'} &nbsp;|&nbsp;
                    🏷 {d.project_id} &nbsp;|&nbsp;
                    ⚙️ {d.status.value if d.status else '—'} &nbsp;|&nbsp;
                    🔧 {', '.join(d.technologies) if d.technologies else 'no technologies'}
                  </div>
                  <div class="statement">{d.statement or '—'}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            with st.expander("Full details + Timeline + Constraints"):
                left, right = st.columns(2)
                with left:
                    st.markdown("**Context summary**")
                    st.write(d.context_summary or "—")
                    st.markdown("**Selected option**")
                    st.code(d.selected_option or "—")
                    if d.reasons:
                        st.markdown("**Reasons**")
                        for r in d.reasons:
                            st.markdown(f"- {r if isinstance(r, str) else r.statement}")
                    if d.participants:
                        st.markdown(f"**Participants:** {', '.join(d.participants)}")
                    if d.constraints:
                        st.markdown("**Extracted Constraints**")
                        for c in d.constraints:
                            if isinstance(c, Constraint):
                                rl_icon = "🔗" if c.is_reason_linked else ""
                                st.markdown(f"- `{c.key}` = `{c.value}` {rl_icon}")
                with right:
                    st.markdown("**Source IDs**")
                    for s in d.source_ids:
                        st.code(s)
                    st.markdown(f"**Extraction Confidence:** {d.extraction_confidence:.0%}")
                    st.markdown("**Timeline**")
                    try:
                        events = backend.get_decision_timeline(did, role)
                        for ev in events:
                            st.markdown(
                                f"🗓 **{ev.occurred_at.strftime('%Y-%m-%d')}** — "
                                f"`{ev.kind.value}` — {ev.title}"
                            )
                            if ev.summary:
                                st.caption(ev.summary)
                    except NotFoundError:
                        st.write("No timeline events.")


def render_ask(backend, role: str, project_id: str) -> None:
    st.markdown("## 💬 Ask Organizational Memory")
    st.markdown(
        "*Ask a question about past decisions, technologies, or constraints. "
        "The system will search organizational memory, compare constraints, "
        "and produce an evidence-backed decision brief.*"
    )

    question = st.text_area(
        "Ask a question about past decisions, technologies, or constraints:",
        placeholder=(
            "e.g. Should we use Kafka for event streaming?\n"
            "Why did we reject GraphQL?\n"
            "What happened after we disabled backups?"
        ),
        height=120,
    )

    projects = backend.list_projects(role)
    proj_ids = [p.project_id for p in projects]
    ask_project = st.selectbox(
        "Context project (current constraints will be compared to historical ones)",
        options=proj_ids if proj_ids else ["—"],
        index=proj_ids.index(project_id) if project_id in proj_ids else 0,
    )

    if st.button("🔍 Generate Decision Brief", type="primary", disabled=not question.strip()):
        with st.spinner("Searching organizational memory and computing drift…"):
            try:
                brief = backend.ask_question(question.strip(), ask_project, role)
            except Exception as e:
                st.error(f"Error generating brief: {e}")
                return

        st.success(f"Brief generated — Query ID: `{brief.query_id}`")
        st.markdown(f"### 📋 Summary\n{brief.answer_summary}")

        # ── Drift card ──
        if brief.drift and brief.drift.score > 0:
            dr = brief.drift
            badge = drift_badge(dr.level.value if hasattr(dr.level, 'value') else str(dr.level))
            border_color = '#ef4444' if 'high' in str(dr.level).lower() else '#f59e0b' if 'medium' in str(dr.level).lower() else '#22c55e'
            st.markdown(
                f"""
                <div style="background:#1e2139;border-radius:8px;padding:1rem;margin:1rem 0;border-left:4px solid {border_color};">
                  <div style="display:flex;justify-content:space-between;align-items:center;">
                    <span style="color:#a5b4fc;font-weight:700;font-size:1.1rem;">⚠ DECISION DRIFT</span>
                    {badge} &nbsp; <span style="color:#94a3b8;font-size:.85rem;">Score: {dr.score:.0%}</span>
                  </div>
                  <div style="color:#cbd5e1;font-size:.9rem;margin-top:.5rem;">{dr.summary}</div>
                  {'<div style="color:#fca5a5;font-size:.85rem;margin-top:.4rem;font-weight:600;">⚠ Reconsideration warranted — original premises materially differ</div>' if dr.reconsideration_warranted else ''}
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Show constraint delta
            if dr.delta and dr.delta.items:
                render_constraint_delta(dr.delta.items)

        # ── Claims ──
        if brief.claims:
            st.markdown("### 📌 Evidence & Analysis")
            for claim in brief.claims:
                etype = claim.epistemic_type.value.upper() if claim.epistemic_type else "CLAIM"
                icon = {"FACT": "📌", "OBSERVATION": "🔭", "INFERENCE": "🔗", "RECOMMENDATION": "💡"}.get(etype, "•")
                st.markdown(f"{icon} **{etype}** — {claim.text}")
                if claim.source_ids:
                    st.caption("Sources: " + ", ".join(f"`{s}`" for s in claim.source_ids))
        else:
            st.info("No claims were synthesized. Try a more specific question or upload relevant documents first.")

        # ── Confidence ──
        if brief.confidence:
            st.markdown("### 📊 Confidence Breakdown")
            cb = brief.confidence
            cols = st.columns(4)
            for col, (lbl, val) in zip(
                cols,
                [
                    ("Evidence Quality", cb.evidence_quality),
                    ("Temporal Relevance", cb.temporal_relevance),
                    ("Source Agreement", cb.source_agreement),
                    ("Completeness", cb.information_completeness),
                ],
            ):
                with col:
                    confidence_bar(val, lbl)

        # ── Source Evidence ──
        if brief.source_ids:
            st.markdown("### 📄 Source Evidence")
            for sid in brief.source_ids:
                try:
                    ev = backend.get_evidence(sid, role)
                    with st.expander(f"📄 {ev.source_id} — {ev.project_id}"):
                        st.write(ev.excerpt)
                        if ev.date:
                            st.caption(ev.date.strftime("%Y-%m-%d"))
                except NotFoundError:
                    st.caption(f"`{sid}` — evidence not found")

        # ── Historical Decision ──
        if brief.historical_decision:
            hd = brief.historical_decision
            st.markdown("### 🕰 Most Relevant Historical Decision")
            st.markdown(
                f"""
                <div class="dec-card">
                  <h4>{hd.title}</h4>
                  <div class="meta">📅 {hd.date.strftime('%Y-%m-%d') if hd.date else '—'} | {hd.project_id} | {hd.status.value if hd.status else '—'}</div>
                  <div class="statement">{hd.statement or '—'}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_projects(backend, role: str, project_id: str) -> None:
    st.markdown("## 📁 Projects & Drift")

    projects = backend.list_projects(role)
    if not projects:
        st.info("No projects loaded. Upload a document to create one.")
        return

    selected_proj = st.selectbox(
        "Select project to inspect",
        options=[p.project_id for p in projects],
        index=0,
    )

    try:
        ctx = backend.get_project_context(selected_proj, role)
    except NotFoundError:
        st.error("Project not found.")
        return

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(f"### {ctx.project_name or ctx.project_id}")
        st.write("**Project ID:**", ctx.project_id)
        st.write("**Last updated:**", ctx.updated_at.strftime("%Y-%m-%d %H:%M") if ctx.updated_at else "—")
        if ctx.constraints:
            st.markdown("**Current Constraints:**")
            if isinstance(ctx.constraints, dict):
                st.json(ctx.constraints)
            elif isinstance(ctx.constraints, list):
                for c in ctx.constraints:
                    if isinstance(c, Constraint):
                        rl_icon = "🔗" if c.is_reason_linked else ""
                        st.markdown(f"- `{c.key}` = `{c.value}` {rl_icon}")
                    else:
                        st.markdown(f"- {c}")
        else:
            st.info("No constraints recorded for this project.")

    with col_b:
        st.markdown("### 🌊 Drift Cards")
        drift_cards = backend.list_drift_cards(selected_proj, role)
        if not drift_cards:
            st.info("No drift detected for this project. This project may not have overlapping constraints with historical decisions.")
        else:
            for dr in drift_cards:
                badge = drift_badge(dr.level.value if hasattr(dr.level, 'value') else str(dr.level))
                border_color = '#ef4444' if 'high' in str(dr.level).lower() else '#f59e0b' if 'medium' in str(dr.level).lower() else '#22c55e'
                st.markdown(
                    f"""
                    <div style="background:#1e2139;border-radius:8px;padding:.8rem 1rem;margin-bottom:.6rem;border-left:4px solid {border_color};">
                      <div style="display:flex;justify-content:space-between;align-items:center;">
                        <span style="color:#a5b4fc;font-weight:600;font-size:.9rem;">{dr.decision_id}</span>
                        {badge} &nbsp; <span style="color:#94a3b8;font-size:.8rem;">score: {dr.score:.0%}</span>
                      </div>
                      <div style="color:#cbd5e1;font-size:.85rem;margin-top:.4rem;">{dr.summary}</div>
                      {'<div style="color:#fca5a5;font-size:.75rem;margin-top:.3rem;">⚠ Reconsideration recommended</div>' if dr.reconsideration_warranted else ''}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                # Expandable constraint delta
                if dr.delta and dr.delta.items:
                    with st.expander(f"Constraint delta for {dr.decision_id}"):
                        render_constraint_delta(dr.delta.items)


def render_memory(backend, role: str) -> None:
    st.markdown("## 🔭 Memory Evolution")
    st.markdown(
        "*Observations are consolidated evidence-grounded beliefs. "
        "They evolve as new evidence is retained across projects.*"
    )

    topic_filter = st.text_input("Filter by topic", placeholder="e.g. kafka, redis, consumer_count…")
    observations = backend.list_observations(role, topic=topic_filter or None)

    if not observations:
        st.info("No observations found. Try a different topic or upload more documents.")
    else:
        st.markdown(f"**{len(observations)} observation(s)**")
        for obs in observations:
            with st.expander(obs.statement, expanded=False):
                left, right = st.columns(2)
                with left:
                    st.metric("Evidence Count", obs.evidence_count)
                    if obs.first_seen:
                        st.caption(f"First seen: {obs.first_seen.strftime('%Y-%m-%d')}")
                    if obs.last_updated:
                        st.caption(f"Last updated: {obs.last_updated.strftime('%Y-%m-%d')}")
                with right:
                    if obs.supporting_source_ids:
                        st.markdown("**Supporting sources:**")
                        for sid in obs.supporting_source_ids[:5]:
                            st.code(sid)


def render_ingest(backend, role: str, project_id: str) -> None:
    st.markdown("## 📥 Ingest New Document")
    st.info(
        "Upload a markdown file or paste content. The system will parse it, "
        "extract decisions, constraints, and technologies, and make them "
        "available across all views immediately."
    )

    col1, col2 = st.columns(2)
    with col1:
        uploaded = st.file_uploader("Upload markdown (.md)", type=["md", "txt"])
        title_input = st.text_input("Document title (optional)")
        proj_input = st.text_input("Project ID (optional — parsed from file if blank)")
    with col2:
        st.markdown("**Or paste content directly:**")
        pasted = st.text_area("Paste markdown content", height=220)

    st.markdown(
        """
        **Tip:** Use the constraint format `key=value` in your documents
        (e.g., `consumer_count=15`, `replay_required=true`) for automatic
        constraint extraction and drift comparison.
        """
    )

    if st.button("⚡ Ingest Document", type="primary"):
        content = ""
        if uploaded:
            content = uploaded.read().decode("utf-8")
        elif pasted.strip():
            content = pasted.strip()
        else:
            st.warning("Please upload a file or paste content.")
            return

        import re, uuid
        default_title = title_input.strip() or re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        if hasattr(default_title, "group"):
            default_title = default_title.group(1).strip()
        elif not isinstance(default_title, str):
            default_title = f"doc-{uuid.uuid4().hex[:6]}"

        meta_proj = re.search(r"\*\*Project\*\*:\s*(.+)", content)
        effective_proj = proj_input.strip() or (meta_proj.group(1).strip().lower().replace(" ", "-") if meta_proj else project_id)

        entry = SourceManifestEntry(
            source_id=f"SRC-UPLOAD-{uuid.uuid4().hex[:6].upper()}",
            project_id=effective_proj,
            source_type=SourceType.adr,
            title=default_title,
            date=datetime.now(tz=UTC),
        )

        with st.spinner("Ingesting and extracting decisions…"):
            result = backend.ingest_source(entry, content, role)

        if result.status.value == "success":
            st.success(
                f"✅ Ingested! Source ID: `{result.source_id}` | "
                f"Memories: {result.memories_created} | Decisions: {result.decisions_extracted}"
            )
            st.rerun()
        else:
            st.error("Ingest failed.")


def render_outcome_chains(backend, role: str) -> None:
    st.markdown("## 🔗 Decision → Outcome Chains")
    st.markdown(
        "*View how decisions connect to downstream outcomes and incidents. "
        "Causal links are labeled with calibrated confidence.*"
    )

    decisions = backend.search_decisions(DecisionFilter(), role)
    if not decisions:
        st.info("No decisions loaded.")
        return

    dec_options = [f"{d.decision_id} — {d.title}" for d in decisions]
    selected = st.selectbox("Select a decision to inspect its outcome chain", dec_options)
    dec_id = selected.split(" — ")[0] if selected else None

    if dec_id:
        try:
            chain = backend.get_outcome_chain(dec_id, role)
        except NotFoundError:
            st.info("No outcome chain found for this decision.")
            return

        if chain.steps:
            st.markdown("### Timeline Steps")
            for i, step in enumerate(chain.steps):
                st.markdown(
                    f"""
                    <div class="chain-step">
                      <strong>{step.title}</strong><br>
                      <span style="color:#94a3b8;font-size:.8rem;">
                        📅 {step.date.strftime('%Y-%m-%d') if step.date else '—'}
                        &nbsp;|&nbsp; Sources: {', '.join(step.source_ids) if step.source_ids else '—'}
                      </span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if i < len(chain.steps) - 1:
                    st.markdown('<div class="chain-link">↓</div>', unsafe_allow_html=True)

        if chain.links:
            st.markdown("### ⚡ Causal Links")
            for link in chain.links:
                label_color = {
                    "explicit_causal_link": "#ef4444",
                    "strong_evidence": "#f59e0b",
                    "possible_causal_link": "#94a3b8",
                }.get(link.label.value, "#94a3b8")

                st.markdown(
                    f"""
                    <div style="background:#1e2139;border-radius:8px;padding:.8rem 1rem;margin:.5rem 0;
                                border-left:3px solid {label_color};">
                      <span style="color:{label_color};font-weight:600;font-size:.85rem;">
                        {link.label.value.upper().replace('_', ' ')}
                      </span>
                      <span style="color:#94a3b8;font-size:.8rem;"> — confidence: {link.confidence:.0%}</span>
                      <div style="color:#cbd5e1;font-size:.88rem;margin-top:.3rem;">{link.rationale}</div>
                      <div style="color:#64748b;font-size:.75rem;margin-top:.2rem;">
                        Evidence: {', '.join(link.evidence_ids) if link.evidence_ids else '—'}
                      </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        elif not chain.steps:
            st.info("No outcome chain data available for this decision.")


def render_review_queue(backend, role: str) -> None:
    st.markdown("## 🔍 Review Queue")
    st.markdown("*Decisions with low extraction confidence or missing reasons need manual verification.*")

    items = backend.list_review_queue(role)
    if not items:
        st.success("✅ No items in the review queue. All decisions have adequate confidence.")
        return

    st.markdown(f"**{len(items)} item(s) need review**")
    for item in items:
        with st.container(border=True):
            st.markdown(f"**{item.title}**  `{item.decision_id}`")
            st.caption(item.reason)
            if item.confidence:
                cb = item.confidence
                cols = st.columns(4)
                for col, (lbl, val) in zip(
                    cols,
                    [
                        ("Evidence Quality", cb.evidence_quality),
                        ("Temporal Relevance", cb.temporal_relevance),
                        ("Source Agreement", cb.source_agreement),
                        ("Completeness", cb.information_completeness),
                    ],
                ):
                    with col:
                        confidence_bar(val, lbl)


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main() -> None:
    backend = _backend()
    role, project_id = render_sidebar(backend)

    pages = [
        "🏠 Overview",
        "🧠 Decisions",
        "💬 Ask Memory",
        "📁 Projects & Drift",
        "🔭 Memory Evolution",
        "🔗 Outcome Chains",
        "📥 Ingest Document",
        "🔍 Review Queue",
    ]

    page = st.tabs(pages)

    with page[0]:
        render_overview(backend, role, project_id)
    with page[1]:
        render_decisions(backend, role, project_id)
    with page[2]:
        render_ask(backend, role, project_id)
    with page[3]:
        render_projects(backend, role, project_id)
    with page[4]:
        render_memory(backend, role)
    with page[5]:
        render_outcome_chains(backend, role)
    with page[6]:
        render_ingest(backend, role, project_id)
    with page[7]:
        render_review_queue(backend, role)


if __name__ == "__main__":
    main()
