from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from memory import refresh_mental_models, wait_for_consolidation
from store import init_database, save_decision, save_source, upsert_project


def _read_manifest(manifest_path: str | os.PathLike[str]) -> list[dict[str, Any]]:
    path = Path(manifest_path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, dict):
        entries = payload.get("entries", [])
        if isinstance(entries, list):
            return entries
        return [payload]
    if isinstance(payload, list):
        return payload
    return []


def seed_from_manifest(manifest_path: str | os.PathLike[str], *, reset: bool = False) -> int:
    """Ingest the demo manifest without duplicating prior records."""
    if reset:
        db_path = os.getenv("DP_DB_PATH")
        if db_path:
            try:
                os.remove(db_path)
            except FileNotFoundError:
                pass

    init_database()

    entries = _read_manifest(manifest_path)
    seen_sources: set[str] = set()
    processed = 0

    for entry in entries:
        project_id = str(entry.get("project_id") or "project-001")
        source_id = str(entry.get("source_id") or entry.get("id") or f"source-{processed + 1}")
        if source_id in seen_sources:
            continue
        seen_sources.add(source_id)

        upsert_project(project_id, project_id)
        save_source(
            source_id,
            project_id,
            source_type=str(entry.get("source_type") or "manifest"),
            title=str(entry.get("title") or source_id),
            hindsight_document_id=source_id,
        )

        decision_id = str(entry.get("decision_id") or source_id)
        save_decision(
            decision_id,
            project_id,
            title=str(entry.get("title") or source_id),
            decision_statement=str(entry.get("text") or ""),
            occurred_at=str(entry.get("occurred_at") or "2025-01-01T00:00:00Z"),
        )
        processed += 1

    try:
        wait_for_consolidation(timeout_s=1.0)
    except Exception:
        pass

    try:
        refresh_mental_models(scope={"allowed_projects": [project_id] if entries else [], "allowed_tags": ["decision", "technology"]})
    except Exception:
        pass

    return processed


def main() -> None:
    manifest_path = os.getenv("DP_MANIFEST_PATH", os.path.join("data", "manifest.json"))
    count = seed_from_manifest(manifest_path)
    print(f"Seeded {count} manifest entries")


if __name__ == "__main__":
    main()
