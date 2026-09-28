"""Visual primitives library — pure SVG and HTML generators for charts, gauges, and stat tiles."""

from __future__ import annotations

import html

from ui.components._theme import render_html

# =========================================================================
# Pure SVG / HTML string primitives (Private, accessible to UI components)
# =========================================================================


def _pill(label: str, bg: str, text_color: str, border: str = "var(--edge)") -> str:
    """Return a soft neo-brutalist pill badge."""
    esc_label = html.escape(str(label))
    border_css = f"border: 1.5px solid {border};" if border else "border: 1.5px solid var(--edge);"
    return (
        f'<span class="dp-badge" style="background:{bg}; color:{text_color}; '
        f"{border_css} border-radius:999px; padding:3px 10px; font-size:0.75rem; "
        f'font-weight:600; display:inline-flex; align-items:center;">{esc_label}</span>'
    )


def _tile(title: str, value: str | int, subtitle: str = "", bg: str = "var(--surface2)") -> str:
    """Return a soft neo-brutalist stat tile with pastel background."""
    esc_title = html.escape(str(title))
    esc_val = html.escape(str(value))
    esc_sub = html.escape(str(subtitle))
    sub_html = (
        f"<div style='font-size:0.75rem; color:var(--muted); margin-top:2px;'>{esc_sub}</div>" if subtitle else ""
    )
    return f"""
    <div style='background:{bg}; border: 1.5px solid var(--edge); border-bottom: 4px solid var(--edge);
                border-radius:16px; padding:1rem 1.15rem; display:flex; flex-direction:column;
                gap:2px;'>
        <div style='font-size:0.8rem; font-weight:600; color:var(--text); text-transform:uppercase; letter-spacing:0.04em;'>
            {esc_title}
        </div>
        <div style='font-size:1.75rem; font-weight:800; color:var(--text); line-height:1.2; font-family:"JetBrains Mono", monospace;'>
            {esc_val}
        </div>
        {sub_html}
    </div>
    """


def _chip(text: str, active: bool = False, on_click_key: str | None = None) -> str:
    """Return a soft neo-brutalist chip."""
    esc_text = html.escape(str(text))
    bg = "var(--coral)" if active else "var(--surface)"
    color = "var(--on-coral)" if active else "var(--text)"
    return (
        f'<span style="background:{bg}; color:{color}; border:1.5px solid var(--edge); '
        f"border-bottom:3px solid var(--edge); border-radius:999px; padding:4px 12px; "
        f'font-size:0.78rem; font-weight:600; display:inline-block; margin:2px;">{esc_text}</span>'
    )


def _svg_ring(value: float, color: str = "var(--blue)", label: str = "", size: int = 48) -> str:
    """Return an SVG progress ring for confidence and score indicators."""
    clamped = max(0.0, min(1.0, float(value)))
    pct = int(clamped * 100)
    radius = (size - 8) / 2
    circ = 2 * 3.14159 * radius
    dashoffset = circ * (1.0 - clamped)
    esc_label = html.escape(label or f"{pct}%")
    return f"""
    <svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" style="display:inline-block; vertical-align:middle;">
        <title>{esc_label}: {pct}%</title>
        <circle cx="{size / 2}" cy="{size / 2}" r="{radius}" fill="none" stroke="var(--line)" stroke-width="4"/>
        <circle cx="{size / 2}" cy="{size / 2}" r="{radius}" fill="none" stroke="{color}" stroke-width="4"
                stroke-dasharray="{circ}" stroke-dashoffset="{dashoffset}" stroke-linecap="round"
                transform="rotate(-90 {size / 2} {size / 2})" style="transition: stroke-dashoffset 0.4s ease;"/>
        <text x="50%" y="54%" text-anchor="middle" dominant-baseline="middle" font-size="{size * 0.26}px"
              font-family="'JetBrains Mono', monospace" font-weight="700" fill="currentColor">{pct}%</text>
    </svg>
    """


def _svg_gauge(
    value: float,
    bands: list[tuple[float, float, str]] | None = None,
    level: str = "",
    width: int = 180,
    height: int = 100,
) -> str:
    """Return an SVG semi-circular drift gauge with indicator needle."""
    clamped = max(0.0, min(1.0, float(value)))
    pct = int(clamped * 100)
    cx, cy, r = width / 2, height - 15, 65
    needle_angle = 180 * clamped
    import math

    rad = math.radians(180 - needle_angle)
    nx = cx + (r - 10) * math.cos(rad)
    ny = cy - (r - 10) * math.sin(rad)

    color_map = {
        "none": "var(--teal)",
        "low": "var(--yellow)",
        "medium": "var(--coral)",
        "high": "var(--coral)",
    }
    gauge_col = color_map.get(level.lower(), "var(--coral)")
    esc_lvl = html.escape(level.upper() if level else f"{pct}%")

    return f"""
    <svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" style="overflow:visible;">
        <title>Drift Score: {pct}% ({esc_lvl})</title>
        <path d="M {cx - r} {cy} A {r} {r} 0 0 1 {cx + r} {cy}" fill="none" stroke="var(--line)" stroke-width="12" stroke-linecap="round"/>
        <path d="M {cx - r} {cy} A {r} {r} 0 0 1 {nx} {ny}" fill="none" stroke="{gauge_col}" stroke-width="12" stroke-linecap="round"/>
        <line x1="{cx}" y1="{cy}" x2="{nx}" y2="{ny}" stroke="var(--edge)" stroke-width="3" stroke-linecap="round"/>
        <circle cx="{cx}" cy="{cy}" r="6" fill="var(--edge)"/>
        <text x="{cx}" y="{cy + 14}" text-anchor="middle" font-size="12px" font-weight="700"
              font-family="'Poppins', sans-serif" fill="currentColor">{pct}% — {esc_lvl}</text>
    </svg>
    """


def _svg_bar_pair(
    old_val: float,
    new_val: float,
    max_val: float | None = None,
    width: int = 240,
    height: int = 24,
) -> str:
    """Return an SVG paired proportional bar showing Then (old) vs Now (new)."""
    v_old = float(old_val)
    v_new = float(new_val)
    m = float(max_val) if max_val else max(v_old, v_new, 1.0)
    w_old = max(4.0, (v_old / m) * (width * 0.4))
    w_new = max(4.0, (v_new / m) * (width * 0.4))
    is_diff = v_old != v_new
    new_col = "var(--coral)" if is_diff else "var(--muted)"

    return f"""
    <svg width="{width}" height="{height}" viewBox="0 0 {width} {height}">
        <title>Old: {old_val} -> New: {new_val}</title>
        <rect x="0" y="4" width="{w_old}" height="14" rx="4" fill="var(--muted)"/>
        <text x="{w_old + 6}" y="15" font-size="11px" font-weight="600" font-family="'JetBrains Mono', monospace" fill="var(--muted)">{old_val}</text>
        <text x="{width * 0.5}" y="15" text-anchor="middle" font-size="12px" font-weight="800" fill="var(--text)">→</text>
        <rect x="{width * 0.55}" y="4" width="{w_new}" height="14" rx="4" fill="{new_col}"/>
        <text x="{width * 0.55 + w_new + 6}" y="15" font-size="11px" font-weight="700" font-family="'JetBrains Mono', monospace" fill="{new_col}">{new_val}</text>
    </svg>
    """


def _svg_step_track(values: list[str], old_val: str, new_val: str, width: int = 260, height: int = 36) -> str:
    """Return an SVG ordinal step track connecting stages with markers moving old->new."""
    if not values:
        values = [old_val, new_val]
    n = len(values)
    spacing = width / max(1, n - 1) if n > 1 else width / 2
    old_idx = values.index(old_val) if old_val in values else 0
    new_idx = values.index(new_val) if new_val in values else n - 1

    steps_svg = []
    for i, val in enumerate(values):
        x = i * spacing if n > 1 else width / 2
        is_old = i == old_idx
        is_new = i == new_idx
        fill = "var(--coral)" if is_new else ("var(--muted)" if is_old else "var(--line)")
        r = 6 if (is_old or is_new) else 4
        steps_svg.append(f'<circle cx="{x}" cy="12" r="{r}" fill="{fill}" stroke="var(--edge)" stroke-width="1.5"/>')
        steps_svg.append(
            f'<text x="{x}" y="28" text-anchor="middle" font-size="9px" font-weight="600" '
            f'font-family="sans-serif" fill="var(--muted)">{html.escape(val)}</text>'
        )

    return f"""
    <svg width="{width}" height="{height}" viewBox="0 0 {width} {height}">
        <title>Track: {old_val} -> {new_val}</title>
        <line x1="0" y1="12" x2="{width}" y2="12" stroke="var(--edge)" stroke-width="1.5"/>
        {"".join(steps_svg)}
    </svg>
    """


def _svg_stacked_bar(segments: list[tuple[str, float, str]], width: int = 280, height: int = 18) -> str:
    """Return an SVG stacked horizontal segment bar."""
    total = sum(val for _, val, _ in segments)
    if total <= 0:
        return f'<svg width="{width}" height="{height}"><rect width="{width}" height="{height}" rx="6" fill="var(--line)"/></svg>'

    curr_x = 0.0
    rects = []
    titles = []
    for label, val, color in segments:
        seg_w = (val / total) * width
        if seg_w > 0:
            rects.append(f'<rect x="{curr_x}" y="0" width="{seg_w}" height="{height}" fill="{color}"/>')
            titles.append(f"{label}: {val}")
            curr_x += seg_w

    title_str = html.escape(", ".join(titles))
    return f"""
    <svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" style="border-radius:6px; overflow:hidden;">
        <title>{title_str}</title>
        {"".join(rects)}
    </svg>
    """


def _svg_donut(segments: list[tuple[str, float, str]], size: int = 80) -> str:
    """Return an SVG donut chart showing breakdown proportions."""
    total = sum(val for _, val, _ in segments)
    if total <= 0:
        return f'<svg width="{size}" height="{size}"><circle cx="{size / 2}" cy="{size / 2}" r="{size / 3}" fill="none" stroke="var(--line)" stroke-width="8"/></svg>'

    radius = size * 0.35
    circ = 2 * 3.14159 * radius
    accum = 0.0
    arcs = []
    titles = []

    for label, val, color in segments:
        fraction = val / total
        dash = fraction * circ
        offset = -(accum * circ)
        arcs.append(
            f'<circle cx="{size / 2}" cy="{size / 2}" r="{radius}" fill="none" stroke="{color}" stroke-width="8" '
            f'stroke-dasharray="{dash} {circ - dash}" stroke-dashoffset="{offset}" transform="rotate(-90 {size / 2} {size / 2})"/>'
        )
        titles.append(f"{label}: {int(val)}")
        accum += fraction

    title_str = html.escape(", ".join(titles))
    return f"""
    <svg width="{size}" height="{size}" viewBox="0 0 {size} {size}">
        <title>{title_str}</title>
        <circle cx="{size / 2}" cy="{size / 2}" r="{radius}" fill="none" stroke="var(--line)" stroke-width="8"/>
        {"".join(arcs)}
    </svg>
    """


def _svg_sparkline(points: list[float | int], color: str = "var(--blue)", width: int = 100, height: int = 26) -> str:
    """Return an SVG sparkline showing progressive metric evolution."""
    if not points or len(points) < 2:
        return f'<svg width="{width}" height="{height}"><line x1="0" y1="{height / 2}" x2="{width}" y2="{height / 2}" stroke="{color}" stroke-width="2"/></svg>'

    min_v = float(min(points))
    max_v = float(max(points))
    spread = max_v - min_v if max_v != min_v else 1.0

    step_x = width / (len(points) - 1)
    pts_coords = []
    dots = []
    for i, p in enumerate(points):
        x = i * step_x
        y = height - 4 - ((float(p) - min_v) / spread) * (height - 8)
        pts_coords.append(f"{x:.1f},{y:.1f}")
        dots.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.5" fill="{color}" stroke="var(--edge)" stroke-width="1"/>')

    polyline_pts = " ".join(pts_coords)
    title_str = html.escape("Evolution: " + " -> ".join(str(p) for p in points))
    return f"""
    <svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" style="overflow:visible;">
        <title>{title_str}</title>
        <polyline fill="none" stroke="{color}" stroke-width="2" points="{polyline_pts}"/>
        {"".join(dots)}
    </svg>
    """


def _svg_funnel(stages: list[tuple[str, int, str]], width: int = 260, height: int = 50) -> str:
    """Return an SVG stepped funnel for ingestion or trace filtering."""
    if not stages:
        return ""
    n = len(stages)
    stage_w = width / n
    rects = []
    titles = []

    for i, (label, count, color) in enumerate(stages):
        x = i * stage_w
        rects.append(
            f'<rect x="{x + 2}" y="8" width="{stage_w - 4}" height="28" rx="6" fill="{color}" '
            f'border="1.5px solid var(--edge)" stroke="var(--edge)" stroke-width="1.5"/>'
        )
        rects.append(
            f'<text x="{x + stage_w / 2}" y="24" text-anchor="middle" font-size="11px" font-weight="700" '
            f'font-family="monospace" fill="var(--on-coral)">{count}</text>'
        )
        rects.append(
            f'<text x="{x + stage_w / 2}" y="44" text-anchor="middle" font-size="9px" font-weight="600" '
            f'font-family="sans-serif" fill="var(--muted)">{html.escape(label)}</text>'
        )
        titles.append(f"{label}: {count}")

    title_str = html.escape(" -> ".join(titles))
    return f"""
    <svg width="{width}" height="{height}" viewBox="0 0 {width} {height}">
        <title>{title_str}</title>
        {"".join(rects)}
    </svg>
    """


def _svg_timeline_axis(events: list[dict[str, str]], width: int = 500, height: int = 40) -> str:
    """Return an SVG horizontal timeline axis with colored kind markers."""
    if not events:
        return ""
    n = len(events)
    step = width / max(1, n - 1) if n > 1 else width / 2
    items = []

    kind_colors = {
        "original_decision": "var(--blue)",
        "exception": "var(--yellow)",
        "outcome": "var(--teal)",
        "reconsideration": "var(--coral)",
        "supersession": "var(--coral)",
    }

    for i, ev in enumerate(events):
        x = i * step if n > 1 else width / 2
        k = ev.get("kind", "original_decision").lower()
        col = kind_colors.get(k, "var(--blue)")
        title = html.escape(ev.get("title", ""))
        date = html.escape(ev.get("date", ""))
        items.append(
            f'<circle cx="{x}" cy="16" r="6" fill="{col}" stroke="var(--edge)" stroke-width="1.5"><title>{title}</title></circle>'
        )
        items.append(
            f'<text x="{x}" y="32" text-anchor="middle" font-size="8.5px" font-family="monospace" fill="var(--muted)">{date}</text>'
        )

    return f"""
    <svg width="{width}" height="{height}" viewBox="0 0 {width} {height}">
        <title>Timeline Axis</title>
        <line x1="0" y1="16" x2="{width}" y2="16" stroke="var(--edge)" stroke-width="2"/>
        {"".join(items)}
    </svg>
    """


# =========================================================================
# Public Streamlit Render Helpers
# =========================================================================


def render_stat_tile(title: str, value: str | int, subtitle: str = "", bg: str = "var(--surface2)") -> None:
    """Render a soft neo-brutalist stat tile component."""
    render_html(_tile(title, value, subtitle, bg))


def render_drift_gauge(drift_score: float, level: str) -> None:
    """Render the prominent drift gauge."""
    render_html(_svg_gauge(drift_score, level=level))


def render_traceability_meter(claims_count: int, sourced_claims_count: int) -> None:
    """Render the PRD 100% traceability meter."""
    pct = int((sourced_claims_count / max(1, claims_count)) * 100)
    render_html(
        f"""
        <div style='display:flex; align-items:center; gap:0.75rem; background:var(--surface);
                    border:1.5px solid var(--edge); border-bottom:3px solid var(--edge);
                    border-radius:12px; padding:0.6rem 0.85rem;'>
            <div>{_svg_ring(sourced_claims_count / max(1, claims_count), color="var(--teal)", size=36)}</div>
            <div>
                <div style='font-size:0.85rem; font-weight:700; color:var(--text);'>
                    Traceability: {sourced_claims_count} of {claims_count} claims grounded ({pct}%)
                </div>
                <div style='font-size:0.72rem; color:var(--muted);'>
                    Every claim traces to primary historical architecture sources
                </div>
            </div>
        </div>
        """
    )
