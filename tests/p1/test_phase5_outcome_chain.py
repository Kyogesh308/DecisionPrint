from __future__ import annotations

from facade import get_outcome_chain, list_drift_cards, list_review_queue
from store import init_database, save_causal_link, save_decision, save_outcome, upsert_project


def test_phase5_outcome_chain_and_drift_cards(tmp_path, monkeypatch):
    db_path = tmp_path / "decisionprint.db"
    import os
    os.environ["DP_DB_PATH"] = str(db_path)
    init_database(str(db_path))

    upsert_project("project-001", "Alpha")
    save_decision(
        "decision-001",
        "project-001",
        title="Kafka rejection",
        decision_statement="Kafka was rejected because the project had two consumers and no replay requirement.",
        occurred_at="2025-01-15T09:30:00Z",
    )
    save_outcome(
        "outcome-001",
        "project-001",
        decision_id="decision-001",
        title="Operational outage",
        summary="No replay outage happened after the architecture refusal.",
    )
    save_causal_link(
        "link-001",
        decision_id="decision-001",
        outcome_id="outcome-001",
        relation="explains",
        evidence_ids=["evidence-1"],
    )

    chain = get_outcome_chain("lead", "decision-001")
    assert chain["decision_id"] == "decision-001"
    assert chain["outcomes"]

    drift_cards = list_drift_cards("lead", "project-001")
    assert isinstance(drift_cards, list)

    review_queue = list_review_queue("lead")
    assert isinstance(review_queue, list)
