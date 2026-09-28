"""Overview page — Enterprise architecture decision intelligence dashboard."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import streamlit as st

from contracts import DecisionFilter, SourceManifestEntry, SourceType
from contracts.ids import make_source_id
from ui.adapters import get_backend
from ui.components import (
    inject_custom_css,
    render_decision_card,
    render_drift_card,
    render_html,
    render_ingest_result,
    render_memory_overview,
    render_sidebar_chrome,
    render_top_bar,
)
from ui.components._state import init_session_state, run_guarded
from ui.components.dialogs import check_and_render_evidence_dialog

init_session_state()

if not st.session_state.get("_top_nav_active"):
    inject_custom_css()
    render_top_bar(active_stage="DECIDE")
    render_sidebar_chrome()

backend = get_backend()
role = st.session_state.get("role") or "admin"

check_and_render_evidence_dialog(backend, role)

# Fetch Memory Overview before header
overview = run_guarded(lambda: backend.get_memory_overview(role))
proj_count = overview.project_count if overview else 0

# 1. Concise Workspace Heading
render_html(
    f"""
    <div style='margin-bottom: 1.5rem;'>
        <h1 style='margin-bottom: 0.25rem;'>Architecture Decision Intelligence</h1>
        <p style='color:var(--muted); font-size:1.02rem; margin:0;'>Memory learned from {proj_count} historical projects</p>
    </div>
    """
)

# 2. Four KPI Cards
if overview:
    render_memory_overview(overview)

# 3. Two-Column Dashboard Grid
left_col, right_col = st.columns([3, 2])

with left_col:
    # Search & Direct Retrieval
    render_html("<div></div>")
    st.markdown("### Search Architectural Decisions")
    st.caption("Search across past ADRs, architecture docs, and meeting records:")

    # Sync with global search if present
    current_search = st.session_state.get("ov_search_input") or st.session_state.get("global_search") or ""

    col_search, col_quick = st.columns([3, 2])
    with col_search:
        search_query = st.text_input(
            "Search query",
            value=current_search,
            placeholder="e.g. Kafka, Redis, backup, tracing...",
            key="ov_search_text_input",
            label_visibility="collapsed",
        )
        if search_query != st.session_state.get("ov_search_input", ""):
            st.session_state.ov_search_input = search_query

    with col_quick:
        q_cols = st.columns(4)
        if q_cols[0].button("Kafka", key="ov_quick_kafka"):
            st.session_state.ov_search_input = "Kafka"
            st.rerun()
        if q_cols[1].button("Redis", key="ov_quick_redis"):
            st.session_state.ov_search_input = "Redis"
            st.rerun()
        if q_cols[2].button("Backup", key="ov_quick_backup"):
            st.session_state.ov_search_input = "backup"
            st.rerun()
        if q_cols[3].button("GraphQL", key="ov_quick_graphql"):
            st.session_state.ov_search_input = "GraphQL"
            st.rerun()

    active_query = st.session_state.get("ov_search_input") or search_query
    if active_query:
        st.markdown(f"**Search Results for:** `{active_query}`")
        results = run_guarded(lambda: backend.search_decisions(DecisionFilter(text=active_query), role))
        if results:
            for dec in results:
                render_decision_card(dec)
        elif results is not None:
            st.info(f"No decisions found matching '{active_query}'.")

    # Document Ingest Expander (Demo Step preserved)
    with st.expander("📥 Ingest New Project Document into Memory", expanded=False):
        st.markdown("#### Ground Organizational Memory in Real Artifacts")
        st.caption("Ingesting documents parses constraints, links decisions to causal outcomes, and updates memory.")

        projects = run_guarded(lambda: backend.list_projects(role))
        proj_options = [p.project_id for p in projects] if projects else ["nova", "alpha", "beta", "gamma", "delta"]

        c1, c2 = st.columns(2)
        with c1:
            selected_proj = st.selectbox(
                "Project Target", proj_options, index=proj_options.index("nova") if "nova" in proj_options else 0
            )
            source_title = st.text_input("Document Title", value="Nova Kickoff — Event Architecture Planning")
        with c2:
            source_types = [e.value for e in SourceType]
            selected_type = st.selectbox("Source Type", source_types, index=source_types.index("meeting_transcript"))
            doc_date = st.date_input("Document Date", value=datetime(2026, 2, 3, tzinfo=UTC))

        # One-click demo button for Nova transcript
        col_demo, col_clear = st.columns([2, 3])
        default_text = ""
        demo_transcript_path = Path("data/current/nova/SRC-NOVA-001_kickoff_event_architecture.md")
        if demo_transcript_path.exists():
            default_text = demo_transcript_path.read_text(encoding="utf-8")

        if col_demo.button("⚡ Load Nova Kickoff Transcript"):
            st.session_state.demo_ingest_content = default_text

        doc_content = st.text_area(
            "Paste transcript, ADR markdown, or design doc:",
            value=st.session_state.get(
                "demo_ingest_content", default_text[:800] if default_text else "Meeting Notes..."
            ),
            height=160,
            label_visibility="collapsed",
        )

        if st.button("🚀 Ingest Document into DecisionPrint", type="primary"):
            with st.spinner("Extracting premises, analyzing causal links, and updating memory..."):
                new_source_id = make_source_id(selected_proj, 99)
                entry = SourceManifestEntry(
                    source_id=new_source_id,
                    project_id=selected_proj,
                    source_type=SourceType(selected_type),
                    title=source_title,
                    file_path=f"current/{selected_proj}/{new_source_id}.md",
                    date=datetime.combine(doc_date, datetime.min.time()),
                    tags=[selected_proj, selected_type, "ingest"],
                    is_current=selected_proj.lower() == "nova",
                )
                res = run_guarded(lambda: backend.ingest_source(entry, doc_content, role))
                if res:
                    render_ingest_result(res)
                    st.balloons()

with right_col:
    # Real Drift Cards for Nova
    drift_cards = run_guarded(lambda: backend.list_drift_cards("nova", role))
    if drift_cards:
        for card in drift_cards:
            render_drift_card(card)
    else:
        st.info("No active decision drift recorded.")

    if st.button("View Details &rarr;", key="btn_view_drift_details", use_container_width=True):
        st.session_state.selected_decision_id = "DEC-ALPHA-001"
        try:
            st.switch_page("pages/1_Ask.py")
        except Exception:  # noqa: BLE001
            st.info("Navigate to 'Ask DecisionPrint' to inspect the Kafka brief.")

    # Quick Actions Panel
    st.markdown("#### Quick Intelligence Actions")
    st.caption("Common architectural audit workflows:")
    if st.button("🔍 Query Memory: 'Should Nova use Kafka?'", use_container_width=True):
        st.session_state.selected_decision_id = "DEC-ALPHA-001"
        try:
            st.switch_page("pages/1_Ask.py")
        except Exception:  # noqa: BLE001, S110
            pass
    if st.button("🏗️ Review Project Nova Active Drift", use_container_width=True):
        try:
            st.switch_page("pages/2_Current_Projects.py")
        except Exception:  # noqa: BLE001, S110
            pass
    if st.button("🔗 Audit Cedar Chain (Backup Incident)", use_container_width=True):
        st.session_state.selected_decision_id = "DEC-DELTA-001"
        try:
            st.switch_page("pages/6_Outcome_Chain.py")
        except Exception:  # noqa: BLE001, S110
            pass
