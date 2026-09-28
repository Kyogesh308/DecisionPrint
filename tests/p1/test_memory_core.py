from __future__ import annotations

import types

import memory as memory_module
from memory import (
    MemoryUnavailableError,
    RecallBundle,
    ReflectResult,
    RetainResult,
    init_memory_bank,
    recall_memories,
    reflect_on_question,
    retain_source,
)


class FakeHindsight:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.calls: list[tuple[str, dict]] = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def create_bank(self, bank_id: str, **kwargs):
        self.calls.append(("create_bank", {"bank_id": bank_id, **kwargs}))
        return {"status": "ok", "bank_id": bank_id}

    def retain(self, *, bank_id: str, document_id: str, content: str, metadata=None, tags=None, **kwargs):
        self.calls.append(
            (
                "retain",
                {
                    "bank_id": bank_id,
                    "document_id": document_id,
                    "content": content,
                    "metadata": metadata or {},
                    "tags": tags or [],
                    **kwargs,
                },
            )
        )
        return {"status": "ok", "document_id": document_id, "memory_ids": ["memory-1"]}

    def recall(self, *, bank_id: str, query: str, limit: int = 20, **kwargs):
        self.calls.append(("recall", {"bank_id": bank_id, "query": query, "limit": limit, **kwargs}))
        return {
            "results": [
                {
                    "text": "Kafka was rejected because the project had two consumers and no replay requirement.",
                    "metadata": {"source_id": "arch-doc-001"},
                }
            ]
        }

    def reflect(self, *, bank_id: str, query: str, context=None, **kwargs):
        self.calls.append(("reflect", {"bank_id": bank_id, "query": query, "context": context, **kwargs}))
        return {"text": "Kafka was rejected under a narrow set of constraints that no longer match the current project."}


def test_init_memory_bank_creates_bank(monkeypatch):
    fake_client = FakeHindsight(base_url="http://localhost:8888")

    def factory(base_url: str):
        assert base_url == "http://localhost:8888"
        return fake_client

    monkeypatch.setattr(memory_module, "Hindsight", factory)
    monkeypatch.setenv("DP_HINDSIGHT_BASE_URL", "http://localhost:8888")
    monkeypatch.setenv("DP_HINDSIGHT_BANK_ID", "northstar-org")

    init_memory_bank()

    assert any(
        call_name == "create_bank"
        and call_kwargs["bank_id"] == "northstar-org"
        and "mission" in call_kwargs
        for call_name, call_kwargs in fake_client.calls
    )


def test_retain_source_and_recall_memories(monkeypatch):
    fake_client = FakeHindsight(base_url="http://localhost:8888")
    monkeypatch.setattr(memory_module, "Hindsight", lambda base_url: fake_client)
    monkeypatch.setenv("DP_HINDSIGHT_BASE_URL", "http://localhost:8888")
    monkeypatch.setenv("DP_HINDSIGHT_BANK_ID", "northstar-org")

    result = retain_source(
        "arch-doc-001",
        "Kafka was rejected because the project had two consumers and no replay requirement.",
        tags=["decision", "technology"],
    )

    assert isinstance(result, RetainResult)
    assert result.source_id == "arch-doc-001"
    assert result.memory_ids == ["memory-1"]
    assert "decision" in result.tags

    bundle = recall_memories("Why was Kafka rejected?", scope={"allowed_tags": ["decision"]})

    assert isinstance(bundle, RecallBundle)
    assert bundle.results[0].text.startswith("Kafka was rejected")
    assert bundle.results[0].source_id == "arch-doc-001"


def test_reflect_on_question_raises_error_when_response_empty(monkeypatch):
    class EmptyReflectHindsight(FakeHindsight):
        def reflect(self, *, bank_id: str, query: str, context=None, **kwargs):
            return {"text": " "}

    fake_client = EmptyReflectHindsight(base_url="http://localhost:8888")
    monkeypatch.setattr(memory_module, "Hindsight", lambda base_url: fake_client)
    monkeypatch.setenv("DP_HINDSIGHT_BASE_URL", "http://localhost:8888")
    monkeypatch.setenv("DP_HINDSIGHT_BANK_ID", "northstar-org")

    try:
        reflect_on_question("Why was Kafka rejected?", scope={"allowed_tags": ["decision"]})
        raise AssertionError("MemoryUnavailableError was not raised")
    except MemoryUnavailableError:
        pass
