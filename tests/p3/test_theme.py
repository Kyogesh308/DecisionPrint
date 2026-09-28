"""Theme regression tests: contrast in both modes, no hard-coded colours outside the theme."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from ui.components._theme import TOKENS, build_css, html_compact


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


def test_html_compact_has_no_indentation_or_blank_lines() -> None:
    """Verify html_compact collapses HTML into a single line without indentation or blank lines."""
    fragment = """
        <div class="test">
            <p>
                Hello World
            </p>
        </div>
    """
    compacted = html_compact(fragment)
    assert "\n" not in compacted
    assert "    " not in compacted
    assert compacted == '<div class="test"><p> Hello World </p></div>'


def test_no_direct_unsafe_markdown() -> None:
    """Verify no UI python files call st.markdown with unsafe_allow_html=True outside _theme.py."""
    offenders = []
    for p in Path("ui").rglob("*.py"):
        if p.name == "_theme.py":
            continue
        content = p.read_text(encoding="utf-8")
        if "unsafe_allow_html" in content:
            offenders.append(str(p))
    assert not offenders, f"Found direct unsafe_allow_html usage outside _theme.py in: {offenders}"


def test_all_css_vars_are_defined() -> None:
    """Extract var(--name) from ui/ files and build_css output and verify all exist in :root."""
    css = build_css("light")
    root_vars = set(re.findall(r"--([a-zA-Z0-9_-]+)\s*:", css))
    used_vars = set()
    for p in Path("ui").rglob("*.py"):
        content = p.read_text(encoding="utf-8")
        used_vars.update(re.findall(r"var\(--([a-zA-Z0-9_-]+)\)", content))
    missing = used_vars - root_vars
    assert not missing, f"CSS variables used in UI but not defined in :root: {missing}"


def test_drift_level_colours_distinct() -> None:
    """Verify drift level colors (teal, yellow, orange, coral) are pairwise distinct and meet AA contrast against ink."""
    for mode in ["light", "dark"]:
        tokens = TOKENS[mode]
        levels = [tokens["teal"], tokens["yellow"], tokens["orange"], tokens["coral"]]
        assert len(set(levels)) == 4, f"{mode}: drift level colors must be pairwise distinct"
        for color in levels:
            assert _ratio(tokens["ink"], color) >= 4.5, f"{mode}: contrast of ink on {color} must be >= 4.5"

