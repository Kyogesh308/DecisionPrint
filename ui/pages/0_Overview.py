"""Overview page — Memory at a glance, decision search, and document ingestion."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import streamlit as st

from contracts import DecisionFilter, SourceManifestEntry, SourceType
from contracts.ids import make_source_id
from ui.adapters import get_backend
from ui.components._theme import inject_custom_css
from ui.components.dialogs import check_and_render_evidence_dialog
from ui.components.renders import render_decision_card, render_ingest_result, render_memory_overview

backend = get_backend()
role = st.session_state.get("role") or "admin"

inject_custom_css()
check_and_render_evidence_dialog(backend, role)

st.title("📊 Organizational Decision Memory Overview")
st.markdown(
    "<p style='color:#94A3B8; font-size:1.1rem;'>Continuous recall, architectural drift tracking, and epistemic grounding across historical projects.</p>",
    unsafe_allow_html=True,
)

# 1. Hero Memory Overview
try:
    overview = backend.get_memory_overview(role)
    render_memory_overview(overview)
except Exception as e:  # noqa: BLE001
    st.error(f"Failed to fetch memory overview: {e}")

st.markdown("---")

# 2. Decision Search
st.subheader("🔍 Search Organizational Decisions")
st.caption("Search across past ADRs, architecture docs, and meeting records. Try searching 'Kafka' for the demo.")

col_search, col_quick = st.columns([3, 2])
with col_search:
    search_query = st.text_input(
        "Search query", value="", placeholder="e.g. Kafka, Redis, backup, tracing...", label_visibility="collapsed"
    )

with col_quick:
    st.markdown("<span style='font-size:0.85rem; color:#94A3B8;'>Quick queries: </span>", unsafe_allow_html=True)
    q_cols = st.columns(4)
    if q_cols[0].button("Kafka"):
        search_query = "Kafka"
    if q_cols[1].button("Redis"):
        search_query = "Redis"
    if q_cols[2].button("Backup"):
        search_query = "backup"
    if q_cols[3].button("GraphQL"):
        search_query = "GraphQL"

if search_query:
    st.markdown(f"**Search Results for:** `{search_query}`")
    try:
        results = backend.search_decisions(DecisionFilter(text=search_query), role)
        if results:
            for dec in results:
                render_decision_card(dec)
        else:
            st.info(f"No decisions found matching '{search_query}'.")
    except Exception as e:  # noqa: BLE001
        st.error(f"Search failed: {e}")

st.markdown("---")

# 3. Document Ingestion Expander (Demo Step 30–45s)
with st.expander("📥 Ingest New Project Document into Memory", expanded=False):
    st.markdown("#### Ground Organizational Memory in Real Artifacts")
    st.caption(
        "Ingesting documents parses constraints, links decisions to causal outcomes, and consolidates higher-order observations."
    )

    try:
        projects = backend.list_projects(role)
        proj_options = [p.project_id for p in projects]
    except Exception:  # noqa: BLE001
        proj_options = ["nova", "alpha", "beta", "gamma", "delta"]

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

    st.markdown("**Document Content:**")

    # One-click demo button for Nova transcript
    col_demo, col_clear = st.columns([2, 3])
    default_text = ""
    demo_transcript_path = Path("data/current/nova/SRC-NOVA-001_kickoff_event_architecture.md")
    if demo_transcript_path.exists():
        default_text = demo_transcript_path.read_text(encoding="utf-8")

    if col_demo.button("⚡ One-Click Demo: Load Nova Kickoff Transcript"):
        st.session_state.demo_ingest_content = default_text

    doc_content = st.text_area(
        "Paste transcript, ADR markdown, or design doc:",
        value=st.session_state.get("demo_ingest_content", default_text[:800] if default_text else "Meeting Notes..."),
        height=200,
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
            try:
                res = backend.ingest_source(entry, doc_content, role)
                render_ingest_result(res)
                st.balloons()
            except Exception as e:  # noqa: BLE001
                st.error(f"Ingestion failed: {e}")
