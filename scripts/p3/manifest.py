"""Manifest tooling — build, write, and validate data/manifest.json."""

from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from pathlib import Path

from contracts import SourceManifestEntry, SourceType

TAGS_BY_SOURCE = {
    "SRC-ALPHA-001": ["messaging", "rabbitmq", "kafka", "architecture"],
    "SRC-ALPHA-002": ["adr", "messaging", "rabbitmq", "decision"],
    "SRC-ALPHA-003": ["meeting", "review-board", "messaging"],
    "SRC-ALPHA-004": ["caching", "redis"],
    "SRC-ALPHA-005": ["observability", "logging"],
    "SRC-ALPHA-006": ["database", "postgres"],
    "SRC-BETA-001": ["queue", "async", "workaround"],
    "SRC-BETA-002": ["api", "graphql", "rest"],
    "SRC-BETA-003": ["observability", "tracing"],
    "SRC-BETA-004": ["auth", "oauth2"],
    "SRC-DELTA-001": ["cost", "infrastructure", "backup"],
    "SRC-DELTA-002": ["backup", "implementation"],
    "SRC-DELTA-003": ["incident", "postmortem", "backup"],
    "SRC-DELTA-004": ["retro", "infrastructure"],
    "SRC-GAMMA-001": ["caching", "redis", "cluster"],
    "SRC-GAMMA-002": ["cdn", "performance"],
    "SRC-NOVA-001": ["event-platform", "kafka", "requirements"],
    "SRC-NOVA-002": ["design", "event-platform", "kafka"],
}


def build_manifest_entries(root_dir: str | Path) -> list[SourceManifestEntry]:
    """Scan historical and current markdown docs and build SourceManifestEntry objects."""
    root_dir = Path(root_dir)
    data_dir = root_dir if (root_dir / "historical").exists() else root_dir / "data"

    entries: list[SourceManifestEntry] = []
    doc_paths = sorted(data_dir.glob("**/*.md"))

    for p in doc_paths:
        if p.name.startswith("."):
            continue
        sid_match = re.search(r"(SRC-[A-Z]+-[0-9]{3})", p.name)
        if not sid_match:
            continue
        sid = sid_match.group(1)
        proj = sid.split("-")[1].lower()

        content = p.read_text(encoding="utf-8")

        m_title = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        title = m_title.group(1).replace("\u2014", "-").replace("\u2013", "-").strip() if m_title else sid

        m_date = re.search(r"\*\*Date:\*\*\s*([0-9-]+)", content)
        date_val = (
            datetime.strptime(m_date.group(1).strip(), "%Y-%m-%d").replace(tzinfo=UTC)
            if m_date
            else datetime(2024, 1, 1, tzinfo=UTC)
        )

        m_type = re.search(r"\*\*Type:\*\*\s*([a-zA-Z_]+)", content)
        type_str = m_type.group(1).strip() if m_type else "architecture_doc"
        source_type = SourceType(type_str) if type_str in {e.value for e in SourceType} else SourceType.architecture_doc

        rel_path = p.relative_to(data_dir).as_posix()
        is_current = proj == "nova"
        sensitivity = "confidential" if sid == "SRC-DELTA-001" else "internal"
        tags = TAGS_BY_SOURCE.get(sid, [proj, type_str])

        entry = SourceManifestEntry(
            source_id=sid,
            project_id=proj,
            source_type=source_type,
            title=title,
            file_path=rel_path,
            date=date_val,
            tags=tags,
            sensitivity=sensitivity,
            is_current=is_current,
        )
        entries.append(entry)

    # Sort deterministically by date then source_id
    entries.sort(key=lambda x: (x.date, x.source_id))
    return entries


def write_manifest(entries: list[SourceManifestEntry], path: str | Path) -> None:
    """Write manifest.json from a list of SourceManifestEntry."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = [e.model_dump(mode="json") for e in entries]
    path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")


def validate_manifest(path: str | Path) -> list[str]:
    """Validate manifest.json and return a list of errors (empty = valid)."""
    path = Path(path)
    errors: list[str] = []

    if not path.exists():
        return [f"Manifest not found: {path}"]

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return [f"Invalid JSON: {e}"]

    if not isinstance(data, list):
        return ["Manifest must be a JSON array"]

    seen_ids: set[str] = set()
    valid_types = {e.value for e in SourceType}

    for i, raw in enumerate(data):
        prefix = f"Entry {i}"

        # Parse as SourceManifestEntry
        try:
            entry = SourceManifestEntry(**raw)
        except Exception as e:  # noqa: BLE001
            errors.append(f"{prefix}: invalid entry — {e}")
            continue

        # SRC-<PROJECT>-<NNN> format
        sid = entry.source_id
        parts = sid.split("-")
        if len(parts) != 3 or parts[0] != "SRC" or not parts[2].isdigit() or len(parts[2]) != 3:
            errors.append(f"{prefix}: bad source_id format '{sid}' — expected SRC-<PROJECT>-<NNN>")

        # Project in source_id must match project_id
        if len(parts) >= 2 and parts[1].lower() != entry.project_id.lower():
            errors.append(f"{prefix}: source_id project '{parts[1]}' != project_id '{entry.project_id}'")

        # Duplicate check
        if sid in seen_ids:
            errors.append(f"{prefix}: duplicate source_id '{sid}'")
        seen_ids.add(sid)

        # Source type valid
        if entry.source_type.value not in valid_types:
            errors.append(f"{prefix}: unknown source_type '{entry.source_type}'")

        # File exists
        candidates = [
            path.parent / entry.file_path,
            path.parent.parent / entry.file_path,
            Path(entry.file_path),
        ]
        if not any(c.exists() for c in candidates):
            errors.append(f"{prefix}: file not found '{entry.file_path}'")

    return errors


if __name__ == "__main__":
    base_dir = Path(__file__).resolve().parent.parent.parent
    data_dir = base_dir / "data"
    manifest_file = data_dir / "manifest.json"

    print("Generating manifest entries...")
    entries = build_manifest_entries(data_dir)
    write_manifest(entries, manifest_file)
    print(f"Wrote {len(entries)} entries to {manifest_file}")

    print("Validating manifest...")
    errs = validate_manifest(manifest_file)
    if errs:
        print("ERRORS:")
        for e in errs:
            print(f"- {e}")
    else:
        print("Manifest is 100% valid! (0 errors)")
