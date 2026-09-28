"""State helpers — guarded fetch, session init, error rendering."""

from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar

import streamlit as st

from contracts.errors import MemoryUnavailableError, NotFoundError, ScopeError

T = TypeVar("T")


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
            "⚠️ Memory backend is unreachable. Switch to **fixture** mode using `DP_BACKEND=fixture` in your `.env` file."
        )
    except Exception as e:  # noqa: BLE001 — intentional UI error boundary
        st.error(f"❌ Unexpected error: {e}")
    return None


def init_session_state() -> None:
    """Initialize all session state keys with defaults."""
    defaults = {
        "role": "admin",
        "theme": "light",
        "project_id": None,
        "last_query_id": None,
        "last_brief": None,
        "selected_decision_id": None,
        "evidence_ref": None,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val
