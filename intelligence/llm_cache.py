from __future__ import annotations

import hashlib, json, logging, os, re, tempfile
from datetime import datetime, timezone
from pathlib import Path

from pydantic import BaseModel

from .config import get_settings

_LOG = logging.getLogger("decisionprint.intelligence.cache")
CACHE_FORMAT = "1"
DEMO_CACHE_DIR = Path(__file__).parent / "demo_cache"


def _live_dir() -> Path:
    return Path(get_settings().cache_dir) / "llm"


def make_cache_key(label: str, prompt: str, schema: type[BaseModel] | None = None) -> str:
    schema_part = json.dumps(schema.model_json_schema(), sort_keys=True) if schema else "text"
    digest = hashlib.sha256(
        "\x1f".join((CACHE_FORMAT, schema_part, prompt)).encode("utf-8")
    ).hexdigest()[:20]
    safe = re.sub(r"[^A-Za-z0-9_.-]+", "-", label).strip("-")[:80] or "call"
    return f"{safe}.{digest}"


def load_cached(key: str) -> str | None:
    legacy_key = key.rsplit(".", 1)[0]
    for directory in (_live_dir(), DEMO_CACHE_DIR):
        for filename in (f"{key}.json", f"{legacy_key}.json"):
            path = directory / filename
            if not path.is_file():
                continue
            try:
                envelope = json.loads(path.read_text("utf-8"))
                if envelope.get("format") == CACHE_FORMAT:
                    return envelope["response"]
                if "json" in envelope:
                    return json.dumps(envelope["json"], ensure_ascii=False)
                if "text" in envelope:
                    return str(envelope["text"])
            except (OSError, ValueError, KeyError):
                _LOG.warning("ignoring unreadable cache entry %s", path.name)
    return None


def store_cached(key: str, *, label: str, kind: str, response: str,
                 schema_name: str | None = None) -> None:
    settings = get_settings()
    envelope = {
        "format": CACHE_FORMAT, "label": label, "kind": kind, "schema": schema_name,
        "provider": settings.llm_provider, "model": settings.llm_model,
        "created_at": datetime.now(timezone.utc).isoformat(), "response": response,
    }
    try:
        directory = _live_dir()
        directory.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=directory, suffix=".tmp")
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(envelope, fh, ensure_ascii=False, sort_keys=True, indent=2)
        os.replace(tmp, directory / f"{key}.json")
    except OSError:
        _LOG.warning("could not write cache entry %s", key)
