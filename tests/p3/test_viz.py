"""Tests for visual primitives library (_viz.py), theme injection, and dynamic navigation badges."""

from __future__ import annotations

from ui.components._theme import badge_html, inject_custom_css, inject_theme
from ui.components._viz import (
    _chip,
    _pill,
    _svg_bar_pair,
    _svg_donut,
    _svg_funnel,
    _svg_gauge,
    _svg_ring,
    _svg_sparkline,
    _svg_stacked_bar,
    _svg_step_track,
    _svg_timeline_axis,
    _tile,
)
from ui.components.shell import get_nav_badges


def test_badge_html_never_renders_causal_none() -> None:
    """Causal badge with value 'none' must return an empty string (never render)."""
    assert badge_html("causal", "none") == ""
    assert badge_html("causal", "") == ""
    assert badge_html("causal", "None") == ""


def test_badge_html_renders_explicit_causal_link() -> None:
    """Explicit causal link must return an HTML badge with EXPLICIT CAUSAL LINK text."""
    html_out = badge_html("causal", "explicit_causal_link")
    assert "EXPLICIT CAUSAL LINK" in html_out
    assert "dp-badge" in html_out


def test_svg_ring_has_title_and_percentage() -> None:
    """_svg_ring must contain <title> text alternative and formatted percentage."""
    ring = _svg_ring(0.85, color="#5B8DEF", label="Confidence")
    assert "<title>" in ring
    assert "85%" in ring
    assert "</svg>" in ring


def test_svg_gauge_has_needle_and_level() -> None:
    """_svg_gauge must contain drift level and percentage in title."""
    gauge = _svg_gauge(0.92, level="high")
    assert "<title>" in gauge
    assert "92%" in gauge
    assert "HIGH" in gauge


def test_svg_bar_pair_renders_old_and_new() -> None:
    """_svg_bar_pair must show old and new values with arrow in title."""
    bars = _svg_bar_pair(2, 15)
    assert "Old: 2 -> New: 15" in bars
    assert "<rect" in bars


def test_svg_step_track_ordinal() -> None:
    """_svg_step_track must render track markers with labels."""
    track = _svg_step_track(["low", "moderate", "high"], "low", "high")
    assert "low" in track
    assert "high" in track
    assert "<line" in track


def test_svg_sparkline_evolution() -> None:
    """_svg_sparkline must render connected points."""
    spark = _svg_sparkline([1, 3, 5, 8], color="#52C4C0")
    assert "<polyline" in spark
    assert "Evolution: 1 -&gt; 3 -&gt; 5 -&gt; 8" in spark


def test_svg_stacked_bar_and_donut() -> None:
    """_svg_stacked_bar and _svg_donut must handle segments."""
    segments = [("World", 10.0, "#5B8DEF"), ("Experience", 5.0, "#52C4C0")]
    stacked = _svg_stacked_bar(segments)
    assert "World: 10.0" in stacked

    donut = _svg_donut(segments)
    assert "World: 10" in donut


def test_svg_funnel_and_timeline_axis() -> None:
    """_svg_funnel and _svg_timeline_axis must produce titles and SVG structures."""
    funnel = _svg_funnel([("Raw", 100, "#5B8DEF"), ("Processed", 40, "#52C4C0")])
    assert "Raw: 100" in funnel

    axis = _svg_timeline_axis([{"title": "ADR-001", "date": "2024-05", "kind": "original_decision"}])
    assert "2024-05" in axis


def test_pill_and_tile_generators() -> None:
    """_pill and _tile generators must produce escaped neo-brutalist HTML."""
    pill = _pill("Active", bg="#EAF8F8", text_color="#0B6A68")
    assert "Active" in pill
    assert "dp-badge" in pill

    tile = _tile("Decisions", 42, subtitle="Extracted from ADRs", bg="#FFF9E6")
    assert "Decisions" in tile
    assert "42" in tile
    assert "Extracted from ADRs" in tile


def test_chip_generator() -> None:
    """_chip must render active and inactive styling."""
    chip_inactive = _chip("Kafka")
    assert "Kafka" in chip_inactive
    chip_active = _chip("Kafka", active=True)
    assert "var(--coral" in chip_active


def test_inject_theme_alias() -> None:
    """inject_theme must be an alias for inject_custom_css."""
    assert inject_theme == inject_custom_css


def test_get_nav_badges_safe_execution() -> None:
    """get_nav_badges must return zero counters when backend is None without error."""
    badges = get_nav_badges(backend=None)
    assert isinstance(badges, dict)
    assert badges["explorer_queue"] == 0
    assert badges["high_drift_count"] == 0
    assert badges["ingest_updated"] is False
