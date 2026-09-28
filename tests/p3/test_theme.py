"""Theme regression tests: contrast in both modes, no hard-coded colours outside the theme."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from ui.components._theme import TOKENS


def _lin(c: int) -> float:
    v = c / 255
    return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4


def _lum(hex_color: str) -> float:
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i : i + 2], 16) for i in (0, 2, 4))
    return 0.2126 * _lin(r) + 0.7152 * _lin(g) + 0.0722 * _lin(b)


def _ratio(a: str, b: str) -> float:
    hi, lo = sorted((_lum(a), _lum(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


PAIRS = [
    ("text", "bg"),
    ("text", "surface"),
    ("text", "surface2"),
    ("muted", "bg"),
    ("muted", "surface"),
    ("muted", "surface2"),
    ("ink", "blue"),
    ("ink", "yellow"),
    ("ink", "teal"),
    ("ink", "coral"),
    ("on_coral", "coral"),
    ("bg", "text"),  # last pair = RECOMMENDATION pill
]


@pytest.mark.parametrize("mode", ["light", "dark"])
@pytest.mark.parametrize(("fg", "bg"), PAIRS)
def test_text_contrast_meets_aa(mode: str, fg: str, bg: str) -> None:
    """Every text/background token pair must reach WCAG AA (4.5:1)."""
    t = TOKENS[mode]
    assert _ratio(t[fg], t[bg]) >= 4.5, f"{mode}: {fg} on {bg}"


def test_no_hardcoded_surface_colours_outside_theme() -> None:
    """Only _theme.py may contain literal black/white/grey surface colours."""
    pattern = re.compile(r"#(?:fff|ffffff|f7f7f7|111|111111|000|000000)\b|:\s*(?:white|black)\b", re.IGNORECASE)
    offenders = [
        str(p)
        for p in Path("ui").rglob("*.py")
        if p.name != "_theme.py" and pattern.search(p.read_text(encoding="utf-8"))
    ]
    assert not offenders, f"Use theme tokens instead of literals in: {offenders}"
