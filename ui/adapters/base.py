"""Adapter base — backend selection."""

import os

from contracts.interfaces import FacadeProtocol


def get_backend() -> FacadeProtocol:
    """Return the configured backend (dummy/manifest, fixture or live)."""
    mode = os.getenv("DP_BACKEND", "dummy")
    if mode in ("dummy", "manifest"):
        from ui.adapters.dummy_backend import ManifestBackend

        return ManifestBackend()
    elif mode == "fixture":
        from ui.adapters.fixture_backend import FixtureBackend

        return FixtureBackend()
    elif mode == "live":
        from ui.adapters.live_backend import LiveBackend

        return LiveBackend()
    else:
        raise ValueError(f"Unknown DP_BACKEND: {mode!r}. Use 'dummy', 'manifest', 'fixture', or 'live'.")
