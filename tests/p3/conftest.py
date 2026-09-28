"""P3 test configuration."""

import pytest


@pytest.fixture(autouse=True)
def use_fixture_backend(monkeypatch: pytest.MonkeyPatch) -> None:
	monkeypatch.setenv("DP_BACKEND", "fixture")
