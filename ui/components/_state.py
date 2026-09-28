"""State helpers — guarded fetch, session init, error rendering."""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime
from typing import TypeVar

import streamlit as st
from pydantic import BaseModel, Field

from contracts import DecisionBrief
from contracts.errors import MemoryUnavailableError, NotFoundError, ScopeError

T = TypeVar("T")


class ChatTurn(BaseModel):
    """One Q&A turn in the Ask thread."""

    question: str
    brief: DecisionBrief | None = None
    error: str | None = None
    query_id: str = ""
    asked_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


def run_guarded(fn: Callable[..., T], *args, **kwargs) -> T | None:
    """Call fn and render friendly UI on contract errors."""
    try:
        return fn(*args, **kwargs)
    except ScopeError:
        st.warning(
            "🔒 Your current role doesn't have access to this resource. Try switching to a different role in the sidebar."
        )
    except NotFoundError:
        st.info("🔍 Nothing found — try a different search or selection.")
    except MemoryUnavailableError:
        st.error(
            "⚠️ Hindsight is unavailable. Check `DP_HINDSIGHT_BASE_URL` and service credentials, or switch to fixture mode with `DP_BACKEND=fixture`."
        )
    except Exception as e:  # noqa: BLE001 — intentional UI error boundary
        st.error(f"❌ Unexpected error: {e}")
    return None


def init_session_state() -> None:
    """Initialize all session state keys with defaults."""
    defaults = {
        "role": "admin",
        "theme": "light",
        "app_theme_radio_sidebar": "light",
        "settings_theme_radio": "light",
        "project_id": None,
        "last_query_id": None,
        "last_brief": None,
        "last_question": None,
        "selected_decision_id": None,
        "evidence_ref": None,
        "global_search": "",
        "ask_input": "Should Nova use Kafka for event streaming?",
        "ov_search_input": "",
        "chat_turns": [],
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val
