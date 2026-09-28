"""Load and validate fixture JSON files against contracts models."""

import json
from pathlib import Path

from contracts.models import (
    CurrentProjectContext,
    Decision,
    RecallBundle,
    SourceRef,
)

FIXTURE_DIR = Path(__file__).parent


def load_decision_alpha_kafka() -> Decision:
    """Load the Alpha project Kafka rejection decision."""
    raw = json.loads(
        (FIXTURE_DIR / "decision_alpha_kafka.json").read_text(encoding="utf-8")
    )
    return Decision.model_validate(raw)


def load_context_nova() -> CurrentProjectContext:
    """Load the Nova project's current constraints."""
    raw = json.loads((FIXTURE_DIR / "context_nova.json").read_text(encoding="utf-8"))
    return CurrentProjectContext.model_validate(raw)


def load_recall_bundle_kafka() -> RecallBundle:
    """Load the recall bundle for the Kafka/Nova query."""
    raw = json.loads(
        (FIXTURE_DIR / "recall_bundle_kafka.json").read_text(encoding="utf-8")
    )
    return RecallBundle.model_validate(raw)


def load_recall_bundle_cedar() -> RecallBundle:
    """Load the recall bundle for the Cedar incident chain."""
    raw = json.loads(
        (FIXTURE_DIR / "recall_bundle_cedar.json").read_text(encoding="utf-8")
    )
    return RecallBundle.model_validate(raw)


def load_decision_graphql() -> Decision:
    """Load the Cedar GraphQL decision (non-reason-linked client_diversity scenario)."""
    raw = json.loads(
        (FIXTURE_DIR / "decision_graphql.json").read_text(encoding="utf-8")
    )
    return Decision.model_validate(raw)


def build_fixture_brief_nova_kafka() -> "DecisionBrief":
    """
    Build the canonical Alpha/Nova Kafka brief from fixtures.
    Uses a deterministic fake reflect_fn — no LLM calls.
    This is the primary integration fixture for P3 UI rendering and Phase 5 eval.
    """
    from contracts.enums import Role
    from contracts.models import ReflectResult, Scope
    from intelligence import build_decision_brief

    decision = load_decision_alpha_kafka()
    context = load_context_nova()
    recall = load_recall_bundle_kafka()

    def fake_reflect_fn(
        question: str, scope: "Scope", *, context: str | None = None
    ) -> ReflectResult:
        """
        Fake reflect_fn that returns a fixed JSON response matching the synthesis schema.
        The memory_ids and source_ids reference the real fixture data.
        """
        synthesis_json = json.dumps(
            {
                "answer_summary": (
                    "The Alpha decision rejected Kafka in 2025 because of only two consumers, "
                    "no replay requirement, and a small ops team. Nova's context has fundamentally "
                    "changed: 15 consumers, mandatory replay for compliance, and a large platform "
                    "team. The foundational premises of the original decision no longer hold."
                ),
                "historical_decisions": [
                    {
                        "text": "In March 2025, Project Alpha rejected Kafka because only two consumers were needed and there was no replay requirement.",
                        "label": "FACT",
                        "memory_ids": ["mem-alpha-001"],
                        "source_refs": [{"source_id": "SRC-ALPHA-001"}],
                    },
                    {
                        "text": "The Alpha decision explicitly noted that with no replay requirement, Kafka's primary differentiating value did not apply.",
                        "label": "FACT",
                        "memory_ids": ["mem-alpha-002"],
                        "source_refs": [{"source_id": "SRC-ALPHA-001"}],
                    },
                    {
                        "text": "The ops team was small with no Kafka expertise, making operational risk the decisive factor against adoption.",
                        "label": "FACT",
                        "memory_ids": ["mem-alpha-001"],
                        "source_refs": [{"source_id": "SRC-ALPHA-001"}],
                    },
                ],
                "observations": [
                    {
                        "text": "Nova has grown to 15 consumers — a 7.5x increase from Alpha's two — fundamentally changing the economics of message queue selection.",
                        "label": "OBSERVATION",
                        "memory_ids": ["mem-nova-001"],
                        "source_refs": [{"source_id": "SRC-NOVA-001"}],
                    },
                    {
                        "text": "Nova now requires mandatory event replay for compliance, directly negating the primary reason Kafka was rejected in Alpha.",
                        "label": "OBSERVATION",
                        "memory_ids": ["mem-nova-001", "mem-alpha-002"],
                        "source_refs": [],
                    },
                ],
                "inferences": [
                    {
                        "text": "The three constraints that drove the original rejection — consumer count, replay requirement, and traffic volume — have all changed direction, suggesting the original decision's reasoning does not transfer to Nova.",
                        "label": "INFERENCE",
                        "memory_ids": ["mem-alpha-001", "mem-nova-001"],
                        "source_refs": [],
                    },
                ],
                "recommendation": {
                    "text": (
                        "Three of the four foundational premises of the Alpha Kafka rejection have materially "
                        "changed (consumer count: 2→15, replay_required: false→true, traffic_volume: moderate→high). "
                        "The original decision was made under fundamentally different conditions. Reconsideration warranted."
                    ),
                    "label": "RECOMMENDATION",
                    "memory_ids": ["mem-alpha-001", "mem-nova-001"],
                    "source_refs": [],
                },
            }
        )
        return ReflectResult(
            text=synthesis_json,
            memory_ids=["mem-alpha-001", "mem-alpha-002", "mem-nova-001"],
            source_refs=[
                SourceRef(source_id="SRC-ALPHA-001"),
                SourceRef(source_id="SRC-NOVA-001"),
            ],
        )

    scope = Scope(
        role=Role.ENGINEER,
        allowed_project_ids=["alpha", "nova"],
        allowed_tags=["org:northstar-systems"],
        visibility_levels=["internal"],
    )

    return build_decision_brief(
        query_id="fixture-nova-kafka-001",
        query="Should Nova use Kafka given the Alpha messaging decision from 2025?",
        scope=scope,
        recall=recall,
        decisions=[decision],
        current=context,
        reflect_fn=fake_reflect_fn,
    )
