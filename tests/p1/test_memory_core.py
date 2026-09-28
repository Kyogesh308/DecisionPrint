from __future__ import annotations

import types

import memory as memory_module
import pytest
from memory import (
    MemoryUnavailableError,
    RecallBundle,
    ReflectResult,
    RetainResult,
    init_memory_bank,
    list_mental_models,
    recall_memories,
    reflect_on_question,
    retain_source,
)


class FakeHindsight:
    def __init__(self, base_url: str, api_key: str | None = None):
        self.base_url = base_url
        self.api_key = api_key
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

    def factory(base_url: str, api_key: str | None = None):
        assert base_url == "http://localhost:8888"
        assert api_key is None
        return fake_client

    monkeypatch.setattr(memory_module, "Hindsight", factory)
    monkeypatch.setenv("DP_HINDSIGHT_BASE_URL", "http://localhost:8888")
    monkeypatch.setenv("DP_HINDSIGHT_API_KEY", "")
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
    monkeypatch.setattr(memory_module, "Hindsight", lambda base_url, api_key=None: fake_client)
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
    monkeypatch.setattr(memory_module, "Hindsight", lambda base_url, api_key=None: fake_client)
    monkeypatch.setenv("DP_HINDSIGHT_BASE_URL", "http://localhost:8888")
    monkeypatch.setenv("DP_HINDSIGHT_BANK_ID", "northstar-org")

    try:
        reflect_on_question("Why was Kafka rejected?", scope={"allowed_tags": ["decision"]})
        raise AssertionError("MemoryUnavailableError was not raised")
    except MemoryUnavailableError:
        pass


def test_memory_client_supports_typed_hindsight_responses(monkeypatch):
    from types import SimpleNamespace

    class TypedHindsight(FakeHindsight):
        def retain(self, **kwargs):
            return SimpleNamespace(operation_ids=["operation-1"])

        def recall(self, **kwargs):
            return SimpleNamespace(
                results=[
                    SimpleNamespace(
                        text="Kafka was rejected under the original constraints.",
                        document_id="arch-doc-001",
                        metadata={"source_id": "arch-doc-001"},
                        tags=["decision"],
                        scores=SimpleNamespace(final=0.91),
                    )
                ]
            )

        def reflect(self, **kwargs):
            return SimpleNamespace(text="The original constraints have changed.")

    fake_client = TypedHindsight(base_url="https://hindsight.example", api_key="test-key")
    monkeypatch.setattr(memory_module, "Hindsight", lambda base_url, api_key=None: fake_client)
    monkeypatch.setenv("DP_HINDSIGHT_BASE_URL", "https://hindsight.example")
    monkeypatch.setenv("DP_HINDSIGHT_API_KEY", "test-key")
    monkeypatch.setenv("DP_HINDSIGHT_BANK_ID", "northstar-org")

    retained = retain_source("arch-doc-001", "Kafka was rejected.")
    recalled = recall_memories("Why was Kafka rejected?")
    reflected = reflect_on_question("What changed?")

    assert fake_client.api_key == "test-key"
    assert retained.memory_ids == ["operation-1"]
    assert recalled.results[0].source_id == "arch-doc-001"
    assert recalled.results[0].retrieval_confidence == 0.91
    assert reflected.text == "The original constraints have changed."


def test_list_mental_models_reads_typed_hindsight_response(monkeypatch):
    from types import SimpleNamespace

    class MentalModelHindsight(FakeHindsight):
        def list_mental_models(self, **kwargs):
            assert kwargs["tags"] == ["decision"]
            return SimpleNamespace(
                items=[
                    SimpleNamespace(
                        id="model-1",
                        name="Architecture choices",
                        content="Operations capacity affects technology adoption.",
                        last_refreshed_at="2025-02-01T00:00:00Z",
                    )
                ]
            )

    fake_client = MentalModelHindsight(base_url="http://localhost:8888")
    monkeypatch.setattr(memory_module, "Hindsight", lambda base_url, api_key=None: fake_client)
    monkeypatch.setenv("DP_HINDSIGHT_BANK_ID", "northstar-org")

    models = list_mental_models(scope={"allowed_tags": ["decision"]})

    assert len(models) == 1
    assert models[0].id == "model-1"


def test_hindsight_transport_errors_become_memory_unavailable(monkeypatch):
    class OfflineHindsight(FakeHindsight):
        def recall(self, **kwargs):
            raise ConnectionError("connection refused")

    fake_client = OfflineHindsight(base_url="http://localhost:8888")
    monkeypatch.setattr(memory_module, "Hindsight", lambda base_url, api_key=None: fake_client)

    with pytest.raises(MemoryUnavailableError, match="Hindsight recall request failed"):
        recall_memories("Why was Kafka rejected?")
