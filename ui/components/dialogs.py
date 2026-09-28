"""Modal dialogs for Evidence and Memory Trace."""

from __future__ import annotations

import streamlit as st

from contracts import EvidenceExcerpt, MemoryTrace
from ui.components.renders import render_evidence_panel, render_memory_trace_drawer


@st.dialog("📄 Evidence Grounding", width="large")
def show_evidence_dialog(evidence: EvidenceExcerpt) -> None:
    """Display modal dialog showing evidence grounding."""
    render_evidence_panel(evidence)


@st.dialog("🔍 Hindsight Memory Retrieval Trace", width="large")
def show_memory_trace_dialog(trace: MemoryTrace) -> None:
    """Display modal dialog showing Hindsight memory recall trace."""
    render_memory_trace_drawer(trace)


def check_and_render_evidence_dialog(backend: object, role: str) -> None:
    """If evidence_ref is set in session state, display the evidence dialog."""
    ref = st.session_state.get("evidence_ref")
    if ref:
        st.session_state.evidence_ref = None
        try:
            ev = backend.get_evidence(ref, role)
            show_evidence_dialog(ev)
        except Exception as e:  # noqa: BLE001
            st.error(f"Could not load evidence for {ref}: {e}")
