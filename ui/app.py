"""Main entry point for DecisionPrint UI — Dynamic Top Navigation & Persistent Context Shell (Stage 3A)."""

from __future__ import annotations

import streamlit as st
from dotenv import load_dotenv

from ui.adapters import get_backend
from ui.components import (
    get_nav_badges,
    inject_theme,
    render_nav_context_bar,
)
from ui.components._state import init_session_state

st.set_page_config(page_title="DecisionPrint", page_icon="🧬", layout="wide")
load_dotenv()


def main() -> None:
    """Run the DecisionPrint application frame with dynamic top navigation."""
    init_session_state()
    st.session_state["_top_nav_active"] = True

    # 1. Inject soft neo-brutalist theme once for the entire application
    inject_theme()

    backend = get_backend()
    role = st.session_state.get("role") or "admin"
    project_id = st.session_state.get("project_id") or "nova"

    # 2. Compute dynamic navigation badges safely
    badges = get_nav_badges(backend, role=role, project_id=project_id)
    review_count = badges.get("explorer_queue", 0)
    drift_count = badges.get("high_drift_count", 0)
    ingest_dot = " •" if badges.get("ingest_updated") else ""

    overview_title = f"Overview{ingest_dot}"
    projects_title = f"Projects ({drift_count})" if drift_count else "Projects"
    explorer_title = f"Explorer ({review_count})" if review_count else "Explorer"

    # 3. Dynamic Navigation using top bar position
    pages = [
        st.Page("pages/0_Overview.py", title=overview_title, icon="📊", default=True),
        st.Page("pages/1_Ask.py", title="Ask", icon="💬"),
        st.Page("pages/2_Current_Projects.py", title=projects_title, icon="📁"),
        st.Page("pages/3_Timeline.py", title="Timeline", icon="⏱️"),
        st.Page("pages/4_Decision_Explorer.py", title=explorer_title, icon="🔍"),
        st.Page("pages/5_Memory_Evolution.py", title="Evolution", icon="🧬"),
        st.Page("pages/6_Outcome_Chain.py", title="Outcome Chain", icon="⛓️"),
        st.Page("pages/7_Settings.py", title="Settings", icon="⚙️"),
    ]

    pg = st.navigation(pages, position="top")

    # 4. Render persistent under-nav context bar
    render_nav_context_bar(backend)

    # 5. Execute active page
    pg.run()


if __name__ == "__main__":
    main()
