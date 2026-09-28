"""Tests for fixture builders data integrity and business rules."""

from __future__ import annotations

from contracts import (
    CausalLabel,
    Decision,
    DecisionBrief,
    DriftLevel,
    DriftResult,
    OutcomeChain,
)
from ui.fixtures import builders


def test_decision_alpha_kafka_validity() -> None:
    """Alpha Kafka rejection decision fixture must be valid and reason-linked."""
    dec = builders.build_fixture_decision_alpha_kafka()
    assert isinstance(dec, Decision)
    assert dec.decision_id == "DEC-ALPHA-001"
    assert dec.selected_option == "RabbitMQ"
    reason_linked = [c for c in dec.constraints if c.is_reason_linked]
    assert len(reason_linked) >= 2


def test_drift_alpha_nova_is_high() -> None:
    """Kafka drift from Alpha to Nova must be HIGH with reconsideration warranted."""
    drift = builders.build_fixture_drift_alpha_nova()
    assert isinstance(drift, DriftResult)
    assert drift.level == DriftLevel.high
    assert drift.reconsideration_warranted is True
    assert drift.score >= 0.85
    # Verify consumer_count and replay_required changed
    changed_keys = {item.key for item in drift.delta.items if item.comparison.value == "changed"}
    assert "consumer_count" in changed_keys
    assert "replay_required" in changed_keys


def test_drift_graphql_holds_rejection() -> None:
    """GraphQL drift from Beta to Nova must be MEDIUM but reconsideration NOT warranted."""
    drift = builders.build_fixture_drift_graphql()
    assert isinstance(drift, DriftResult)
    assert drift.level == DriftLevel.medium
    assert drift.reconsideration_warranted is False


def test_cedar_outcome_chain_has_explicit_causal_link() -> None:
    """Cedar chain must feature an EXPLICIT_CAUSAL_LINK from the postmortem."""
    chain = builders.build_fixture_outcome_chain_cedar()
    assert isinstance(chain, OutcomeChain)
    assert chain.decision_id == "DEC-DELTA-001"
    assert len(chain.steps) >= 4

    # Must contain explicit_causal_link
    explicit_links = [link for link in chain.links if link.label == CausalLabel.explicit_causal_link]
    assert len(explicit_links) == 1
    assert "SRC-DELTA-003" in explicit_links[0].evidence_ids
    assert "postmortem" in explicit_links[0].rationale.lower()


def test_brief_nova_kafka_structure() -> None:
    """Master demo brief must combine context, decision, drift, epistemic claims, and confidence."""
    brief = builders.build_fixture_brief_nova_kafka()
    assert isinstance(brief, DecisionBrief)
    assert brief.query_id == "q-nova-kafka-001"
    assert brief.historical_decision is not None
    assert brief.drift is not None
    assert brief.drift.level == DriftLevel.high
    assert len(brief.claims) >= 4
    assert brief.confidence is not None
    assert brief.confidence.evidence_quality is not None
