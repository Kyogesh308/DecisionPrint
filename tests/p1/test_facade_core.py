from __future__ import annotations

from facade import ask_question, ingest_source
from store import ScopeError, init_database, resolve_scope


def test_ingest_source_and_ask_question_round_trip(tmp_path, monkeypatch):
    db_path = tmp_path / "decisionprint.db"
    import os
    os.environ["DP_DB_PATH"] = str(db_path)
    init_database(str(db_path))

    from facade import update_project_context

    class FakeHindsight:
        def __init__(self, base_url: str):
            self.base_url = base_url

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def retain(self, *, bank_id: str, document_id: str, content: str, metadata=None, tags=None, **kwargs):
            return {"status": "ok", "document_id": document_id, "memory_ids": [f"memory-{document_id}"]}

        def recall(self, *, bank_id: str, query: str, limit: int = 20, **kwargs):
            return {
                "results": [
                    {
                        "text": "Kafka was rejected because the project had two consumers and no replay requirement.",
                        "metadata": {"source_id": "source-001", "tags": ["decision"]},
                    }
                ]
            }

        def reflect(self, *, bank_id: str, query: str, context=None, **kwargs):
            return {"text": "Kafka was rejected under narrow constraints that no longer match the current project."}

        def create_bank(self, bank_id: str, **kwargs):
            return {"status": "ok", "bank_id": bank_id}

    import memory
    monkeypatch.setattr(memory, "Hindsight", FakeHindsight)

    result = ingest_source(
        "lead",
        {
            "project_id": "project-001",
            "source_id": "source-001",
            "source_type": "architecture_doc",
            "title": "Kafka decision",
            "is_current": True,
        },
        "Kafka was rejected because the project had two consumers and no replay requirement.",
    )

    assert result["source_id"] == "source-001"
    assert result["project_id"] == "project-001"

    brief = ask_question("lead", "project-001", "Why was Kafka rejected?")

    assert "Kafka" in brief["answer"]
    assert brief["project_id"] == "project-001"
    assert brief["decision_ids"]

    update_project_context("project-001", consumer_count=15, replay_required=True)
    scope = resolve_scope("lead")
    assert scope.role == "lead"


def test_ingest_source_rejects_unauthorized_project():
    import os
    os.environ["DP_DB_PATH"] = os.path.join(os.getcwd(), "var", "decisionprint-facade.db")
    from facade import ingest_source

    try:
        ingest_source(
            "viewer",
            {"project_id": "blocked-project", "source_id": "blocked-source", "source_type": "architecture_doc"},
            "This should be blocked.",
        )
        raise AssertionError("ScopeError was not raised")
    except ScopeError:
        pass
