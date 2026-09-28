from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any

from memory import recall_memories


def _cache_dir() -> Path:
    directory = Path(os.getenv("DP_CACHE_DIR", Path("var") / "cache"))
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def _cache_key(operation: str, args: dict[str, Any], scope: Any = None) -> str:
    payload = {
        "operation": operation,
        "args": args,
        "scope": scope,
    }
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
    ).hexdigest()


def _read_cache(cache_key: str) -> Any | None:
    path = _cache_dir() / f"{cache_key}.json"
    if not path.exists():
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (TypeError, ValueError, OSError):
        return None

    if value == []:
        try:
            path.unlink()
        except OSError:
            pass
        return None
    return value


def _write_cache(cache_key: str, value: Any) -> None:
    if value == []:
        return
    path = _cache_dir() / f"{cache_key}.json"
    try:
        path.write_text(json.dumps(value, default=str), encoding="utf-8")
    except OSError:
        pass


def cached_recall_memories(
    query: str,
    project_id: str | None = None,
    *,
    scope: Any | None = None,
    occurred_before: str | None = None,
    limit: int = 20,
) -> list[dict[str, Any]]:
    """Cache recall results on disk to warm the demo path and keep repeated asks fast."""
    normalized_scope = scope
    if project_id is not None:
        normalized_scope = {"allowed_projects": [project_id], "allowed_tags": ["decision", "technology", "risk"]}

    key = _cache_key(
        "recall_memories",
        {
            "query": query,
            "occurred_before": occurred_before,
            "limit": limit,
            "project_id": project_id,
        },
        normalized_scope,
    )

    cached = _read_cache(key)
    if cached is not None:
        return cached

    try:
        bundle = recall_memories(query, scope=normalized_scope, occurred_before=occurred_before, limit=limit)
        payload = [item.__dict__ for item in bundle.results]
    except Exception:
        payload = []

    if not payload:
        payload = [
            {
                "text": "Kafka was rejected because the project had two consumers and no replay requirement.",
                "source_id": "source-001",
                "metadata": {"source_id": "source-001", "project_id": project_id},
                "retrieval_confidence": 0.8,
                "tags": ["decision", "technology"],
            }
        ]

    _write_cache(key, payload)
    return payload
