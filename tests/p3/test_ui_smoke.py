"""Smoke tests for Streamlit application pages."""

from __future__ import annotations

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def test_app_landing_smoke() -> None:
    """ui/app.py must run without uncaught exceptions."""
    app_path = REPO_ROOT / "ui" / "app.py"
    at = AppTest.from_file(str(app_path), default_timeout=15)
    at.run()
    assert not at.exception


@pytest.mark.parametrize(
    "rel_page_path",
    [
        "ui/pages/0_Overview.py",
        "ui/pages/1_Ask.py",
        "ui/pages/2_Current_Projects.py",
        "ui/pages/3_Timeline.py",
        "ui/pages/4_Decision_Explorer.py",
        "ui/pages/5_Memory_Evolution.py",
        "ui/pages/6_Outcome_Chain.py",
        "ui/pages/7_Settings.py",
    ],
)
def test_all_pages_smoke(rel_page_path: str) -> None:
    """All 8 Streamlit pages must render without exceptions in fixture mode."""
    page_path = REPO_ROOT / rel_page_path
    at = AppTest.from_file(str(page_path), default_timeout=15)
    at.run()
    assert not at.exception, f"Exception occurred while rendering {rel_page_path}: {at.exception}"


@pytest.mark.parametrize(
    "rel_page_path",
    [
        "ui/pages/0_Overview.py",
        "ui/pages/1_Ask.py",
        "ui/pages/2_Current_Projects.py",
        "ui/pages/3_Timeline.py",
        "ui/pages/4_Decision_Explorer.py",
        "ui/pages/5_Memory_Evolution.py",
        "ui/pages/6_Outcome_Chain.py",
        "ui/pages/7_Settings.py",
    ],
)
def test_all_pages_with_initialized_session_state(rel_page_path: str) -> None:
    """All 8 Streamlit pages must render cleanly when session state has default None values (G9 regression test)."""
    page_path = REPO_ROOT / rel_page_path
    at = AppTest.from_file(str(page_path), default_timeout=15)
    at.session_state["role"] = "admin"
    at.session_state["project_id"] = None
    at.session_state["last_query_id"] = None
    at.session_state["last_brief"] = None
    at.session_state["selected_decision_id"] = None
    at.session_state["evidence_ref"] = None
    at.run()
    assert not at.exception, f"Exception with default session state in {rel_page_path}: {at.exception}"
