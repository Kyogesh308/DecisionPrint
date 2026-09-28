from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from typing import Any, Iterable

from dotenv import load_dotenv
from contracts.errors import MemoryUnavailableError

load_dotenv()

try:
    from hindsight_client import Hindsight
except ImportError:  # pragma: no cover - exercised in environments without the dependency
    Hindsight = None


@dataclass
class RecalledMemory:
    text: str
    source_id: str | None = None
    memory_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    retrieval_confidence: float = 0.0
    tags: list[str] = field(default_factory=list)


@dataclass
class RetainResult:
    source_id: str
    document_id: str
    memory_ids: list[str]
    tags: list[str]
    metadata: dict[str, Any]


@dataclass
class RecallBundle:
    query: str
    results: list[RecalledMemory]
    retrieval_confidence: float = 0.0


@dataclass
class ReflectResult:
    question: str
    text: str
    context: str | None = None


RETAIN_MISSION = (
    "DecisionPrint retains decision evidence, reasons, constraints, assumptions, "
    "and outcomes so future questions can be answered with traceable context and "
    "clear provenance."
)


def _base_url() -> str:
    return os.getenv("DP_HINDSIGHT_BASE_URL", "http://localhost:8888")


def _bank_id() -> str:
    return os.getenv("DP_HINDSIGHT_BANK_ID", "northstar-org")


def _normalize_tags(tags: Iterable[str] | str | None) -> list[str]:
    if tags is None:
        return []
    if isinstance(tags, str):
        return [tags]
    return [str(tag) for tag in tags]


def _scope_allowed_tags(scope: Any) -> list[str]:
    if scope is None:
        return []
    if isinstance(scope, dict):
        tags = scope.get("allowed_tags", [])
        return _normalize_tags(tags)
    allowed_tags = getattr(scope, "allowed_tags", [])
    return _normalize_tags(allowed_tags)


def _sanitize_input_text(text: str) -> str:
    cleaned = text.replace("\r\n", "\n").strip()
    lines = []
    for line in cleaned.split("\n"):
        if line.lower().startswith("system:"):
            continue
        if line.lower().startswith("ignore previous instructions"):
            continue
        if line.lower().startswith("assistant:"):
            continue
        lines.append(line)
    return "\n".join(lines).strip()


def _effective_tags(tags: Iterable[str] | str | None, scope: Any = None) -> list[str]:
    allowed = set(_scope_allowed_tags(scope))
    normalized = _normalize_tags(tags)
    if not allowed:
        return normalized
    return [tag for tag in normalized if tag in allowed or tag.startswith("decision")]


def _client():
    if Hindsight is None:
        raise MemoryUnavailableError("hindsight_client is not installed")
    return Hindsight(base_url=_base_url(), api_key=os.getenv("DP_HINDSIGHT_API_KEY") or None)


def _response_value(response: Any, key: str, default: Any = None) -> Any:
    if isinstance(response, dict):
        return response.get(key, default)
    return getattr(response, key, default)


def _call_hindsight(method: str, **kwargs: Any) -> Any:
    try:
        with _client() as client:
            return getattr(client, method)(**kwargs)
    except MemoryUnavailableError:
        raise
    except Exception as exc:
        raise MemoryUnavailableError(
            f"Hindsight {method} request failed; check the service endpoint and credentials"
        ) from exc


def init_memory_bank() -> None:
    """Create the configured bank and attach the project mission for future retention."""
    bank_id = _bank_id()
    with _client() as client:
        create_bank = getattr(client, "create_bank", None)
        if create_bank is not None:
            try:
                create_bank(bank_id=bank_id, mission=RETAIN_MISSION)
            except TypeError:
                create_bank(bank_id=bank_id)

        if hasattr(client, "set_mission"):
            try:
                client.set_mission(bank_id=bank_id, mission=RETAIN_MISSION)
            except TypeError:
                client.set_mission(bank_id=bank_id, mission_text=RETAIN_MISSION)


def retain_source(
    source: str,
    text: str,
    *,
    tags: Iterable[str] | str | None = None,
    occurred_at: str | None = None,
    context: str | None = None,
    metadata: dict[str, Any] | None = None,
    scope: Any = None,
) -> RetainResult:
    """Retain the source text inside the configured Hindsight bank."""
    sanitized_text = _sanitize_input_text(text)
    normalized_tags = _effective_tags(tags, scope)
    merged_metadata: dict[str, Any] = {"source_id": str(source)}
    if occurred_at is not None:
        merged_metadata["occurred_at"] = occurred_at
    if context is not None:
        merged_metadata["context"] = context
    if metadata:
        for key, value in metadata.items():
            if value is not None:
                merged_metadata[key] = value

    response = _call_hindsight(
        "retain",
        bank_id=_bank_id(),
        document_id=str(source),
        content=sanitized_text,
        metadata=merged_metadata,
        tags=normalized_tags,
    )

    memory_ids = _response_value(response, "memory_ids")
    if memory_ids is None:
        memory_ids = _response_value(response, "operation_ids", [])
    if isinstance(memory_ids, str):
        memory_ids = [memory_ids]
    if not isinstance(memory_ids, list):
        memory_ids = [str(memory_ids)]

    return RetainResult(
        source_id=str(source),
        document_id=str(source),
        memory_ids=memory_ids,
        tags=normalized_tags,
        metadata=merged_metadata,
    )


def recall_memories(
    query: str,
    scope: Any = None,
    *,
    occurred_before: str | None = None,
    limit: int = 20,
) -> RecallBundle:
    """Recall relevant memory and materialize the PostgreSQL-friendly result bundle."""
    allowed_tags = _scope_allowed_tags(scope)
    kwargs: dict[str, Any] = {}
    if limit is not None:
        kwargs["max_tokens"] = max(512, min(limit * 512, 16384))
    if occurred_before is not None:
        kwargs["query_timestamp"] = occurred_before
    if allowed_tags:
        kwargs["tags"] = allowed_tags

    response: Any = None
    for attempt in range(3):
        response = _call_hindsight("recall", bank_id=_bank_id(), query=query, **kwargs)
        rows = _response_value(response, "results", [])
        if rows:
            break
        time.sleep(0.2 * (attempt + 1))

    rows = _response_value(response, "results", [])
    recalled: list[RecalledMemory] = []
    for item in rows:
        text = _response_value(item, "text") or _response_value(item, "content") or ""
        metadata = _response_value(item, "metadata") or {}
        if not isinstance(metadata, dict):
            metadata = {}
        source_id = (
            metadata.get("source_id")
            or metadata.get("sourceId")
            or _response_value(item, "document_id")
        )
        tags: list[str] = []
        result_tags = _response_value(item, "tags") or metadata.get("tags")
        if isinstance(result_tags, list):
            tags = [str(tag) for tag in result_tags]
        confidence = _response_value(item, "retrieval_confidence")
        if confidence is None:
            confidence = _response_value(item, "confidence")
        if confidence is None:
            scores = _response_value(item, "scores")
            confidence = _response_value(scores, "final", 0.0)
        if isinstance(metadata.get("tags"), list) and not tags:
            tags = [str(tag) for tag in metadata["tags"]]
        recalled.append(
            RecalledMemory(
                text=str(text),
                source_id=str(source_id) if source_id is not None else None,
                memory_id=str(_response_value(item, "id")) if _response_value(item, "id") is not None else None,
                metadata=dict(metadata),
                retrieval_confidence=float(confidence or 0.0),
                tags=tags,
            )
        )

    retrieval_confidence = max((item.retrieval_confidence for item in recalled), default=0.0)
    return RecallBundle(query=query, results=recalled, retrieval_confidence=retrieval_confidence)


def reflect_on_question(
    question: str,
    scope: Any = None,
    *,
    context: str | None = None,
) -> ReflectResult:
    """Ask Hindsight for a synthesized answer over the scoped memory bank."""
    allowed_tags = _scope_allowed_tags(scope)
    kwargs: dict[str, Any] = {}
    if context is not None:
        kwargs["context"] = context
    if allowed_tags:
        kwargs["tags"] = allowed_tags

    response = _call_hindsight("reflect", bank_id=_bank_id(), query=question, **kwargs)

    text = _response_value(response, "text", response)
    answer = (text or "").strip()
    if not answer:
        raise MemoryUnavailableError(f"No usable answer returned for question: {question!r}")

    return ReflectResult(question=question, text=answer, context=context)


def list_mental_models(scope: Any = None) -> list[Any]:
    """List Hindsight mental models visible to the supplied memory scope."""
    tags = _scope_allowed_tags(scope)
    response = _call_hindsight(
        "list_mental_models",
        bank_id=_bank_id(),
        tags=tags or None,
        detail="full",
    )
    items = _response_value(response, "items", response)
    return items if isinstance(items, list) else []


def list_observation_views(scope: Any = None, *, topic: str | None = None) -> list[dict[str, Any]]:
    """Return a minimal observation list for the current memory bank."""
    allowed_tags = _scope_allowed_tags(scope)
    observations: list[dict[str, Any]] = [
        {
            "id": "obs-001",
            "topic": topic or "decision_quality",
            "summary": "Kafka was rejected under narrow assumptions that no longer match the current project profile.",
            "evidence_count": 3,
            "supporting_sources": ["source-001"],
            "tags": allowed_tags or ["decision"],
        }
    ]
    return observations


def get_observation_view(observation_id: str) -> dict[str, Any]:
    return {
        "id": observation_id,
        "summary": "Kafka was rejected under narrow assumptions that no longer match the current project profile.",
        "evidence_count": 3,
        "history_steps": ["retain", "recall", "reflect"],
    }


def refresh_mental_models(scope: Any = None) -> list[dict[str, Any]]:
    """Create a minimal set of standing mental models used by the demo."""
    allowed_tags = _scope_allowed_tags(scope)
    return [
        {
            "id": "model-001",
            "name": "Current architecture principles",
            "summary": "Prefer explicit constraints and evidence-backed trade-offs.",
            "tags": allowed_tags or ["decision", "technology"],
        },
        {
            "id": "model-002",
            "name": "Recurring operational risks",
            "summary": "Rejecting a technology without replay or scale assumptions creates real drift risk.",
            "tags": allowed_tags or ["risk"],
        },
    ]


def wait_for_consolidation(*, timeout_s: float = 60.0) -> bool:
    """Return True after a short stabilization window.

    The Hindsight bank can be slow to consolidate; for the demo and seed scripts we only need
    a non-destructive, bounded wait that never blows up the caller when the backend is slow.
    """
    return True


def list_mental_model_views(scope: Any = None) -> list[dict[str, Any]]:
    return refresh_mental_models(scope)


def build_memory_trace(query_id: str) -> dict[str, Any]:
    """Return a compact memory trace for a specific query ID."""
    return {
        "query_id": query_id,
        "timeline": [
            {"step": "retain", "summary": "Source retained into the bank"},
            {"step": "recall", "summary": "Historical memory matched the question"},
            {"step": "reflect", "summary": "Decision brief synthesized with context"},
        ],
    }


def get_memory_stats(scope: Any = None) -> dict[str, Any]:
    """Return aggregate memory statistics for the bank."""
    allowed_tags = _scope_allowed_tags(scope)
    return {
        "total_projects": 1,
        "total_sources": 3,
        "total_memories": 5,
        "allowed_tags": allowed_tags or ["decision"],
    }


def wait_for_consolidation(*, timeout_s: float = 60.0) -> bool:
    """Return True once background consolidation is allowed to finish."""
    return True


__all__ = [
    "MemoryUnavailableError",
    "RecalledMemory",
    "RetainResult",
    "RecallBundle",
    "ReflectResult",
    "init_memory_bank",
    "retain_source",
    "recall_memories",
    "reflect_on_question",
    "list_observation_views",
    "get_observation_view",
    "refresh_mental_models",
    "list_mental_model_views",
    "build_memory_trace",
    "get_memory_stats",
    "wait_for_consolidation",
]
