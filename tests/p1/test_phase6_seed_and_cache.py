from __future__ import annotations

import json
import sqlite3

from memory.cache import cached_recall_memories
from scripts.p1.seed_demo import seed_from_manifest


def test_seed_from_manifest_is_idempotent_and_cache_works(tmp_path, monkeypatch):
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(
        json.dumps(
            [
                {
                    "project_id": "project-001",
                    "source_id": "source-001",
                    "title": "Kafka decision",
                    "text": "Kafka was rejected because the project had two consumers and no replay requirement.",
                    "tags": ["decision", "technology"],
                    "occurred_at": "2025-01-15T09:30:00Z",
                }
            ]
        )
    )

    db_path = tmp_path / "decisionprint.db"
    monkeypatch.setenv("DP_DB_PATH", str(db_path))

    first_count = seed_from_manifest(str(manifest_path))
    second_count = seed_from_manifest(str(manifest_path))
    assert first_count == 1
    assert second_count == 1

    with sqlite3.connect(str(db_path)) as conn:
        count = conn.execute("SELECT COUNT(*) FROM sources").fetchone()[0]
    assert count == 1

    cached = cached_recall_memories("Why was Kafka rejected?", "project-001")
    assert isinstance(cached, list)
    assert cached
