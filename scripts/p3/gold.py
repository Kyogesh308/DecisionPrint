"""Gold labels — build evaluation data from the corpus bible."""

from __future__ import annotations

import json
from pathlib import Path

# === Decisions gold labels ===
GOLD_DECISIONS = [
    {
        "decision_id": "DEC-ALPHA-001",
        "project": "alpha",
        "chain": "kafka",
        "title": "Reject Kafka for messaging",
        "selected_option": "RabbitMQ",
        "status": "active",
        "key_constraints": ["consumer_count", "replay_required", "ops_capacity"],
        "reason_linked_constraints": ["consumer_count", "ops_capacity", "replay_required"],
    },
    {
        "decision_id": "DEC-ALPHA-002",
        "project": "alpha",
        "chain": "redis",
        "title": "Single Redis instance",
        "selected_option": "Single Redis",
        "status": "active",
        "key_constraints": ["instance_count", "cache_hit_ratio"],
        "reason_linked_constraints": ["instance_count"],
    },
    {
        "decision_id": "DEC-ALPHA-003",
        "project": "alpha",
        "chain": "tracing",
        "title": "Structured logging over tracing",
        "selected_option": "Structured logging (ELK)",
        "status": "active",
        "key_constraints": ["observability_maturity", "debugging_frequency"],
        "reason_linked_constraints": ["observability_maturity", "debugging_frequency"],
    },
    {
        "decision_id": "DEC-BETA-001",
        "project": "beta",
        "chain": "graphql",
        "title": "Reject GraphQL for API layer",
        "selected_option": "REST",
        "status": "active",
        "key_constraints": ["client_count", "client_diversity", "schema_complexity"],
        "reason_linked_constraints": ["client_count", "schema_complexity"],
    },
    {
        "decision_id": "DEC-GAMMA-001",
        "project": "gamma",
        "chain": "redis",
        "title": "Scale to Redis Cluster",
        "selected_option": "Redis Cluster (4 nodes)",
        "status": "active",
        "key_constraints": ["instance_count", "cache_hit_ratio", "session_persistence"],
        "reason_linked_constraints": ["cache_hit_ratio"],
    },
    {
        "decision_id": "DEC-DELTA-001",
        "project": "delta",
        "chain": "cedar",
        "title": "Remove automated backups",
        "selected_option": "Disable automated backups",
        "status": "superseded",
        "key_constraints": ["backup_policy", "budget_pressure", "data_criticality"],
        "reason_linked_constraints": ["budget_pressure"],
    },
]

# === Constraints gold labels ===
GOLD_CONSTRAINTS = {
    "alpha": {
        "consumer_count": "2",
        "replay_required": "false",
        "traffic_volume": "moderate",
        "ops_capacity": "small",
        "async_workflows": "false",
        "instance_count": "1",
        "cache_hit_ratio": "0.85",
        "session_persistence": "false",
        "observability_maturity": "logs_only",
        "debugging_frequency": "weekly",
        "incident_mttr": "4h",
    },
    "beta": {
        "client_count": "3",
        "client_diversity": "internal_only",
        "schema_complexity": "low",
        "consumer_count": "5",
        "async_workflows": "limited",
        "observability_maturity": "partial_tracing",
        "debugging_frequency": "daily",
        "incident_mttr": "2h",
    },
    "gamma": {
        "instance_count": "4",
        "cache_hit_ratio": "0.72",
        "session_persistence": "true",
    },
    "delta": {
        "backup_policy": "none",
        "budget_pressure": "high",
        "data_criticality": "medium",
    },
    "nova": {
        "consumer_count": "15",
        "replay_required": "true",
        "traffic_volume": "high",
        "ops_capacity": "medium",
        "async_workflows": "true",
        "instance_count": "20",
        "cache_hit_ratio": "target 0.90",
        "session_persistence": "true",
        "client_count": "12",
        "client_diversity": "partner_ecosystem",
        "schema_complexity": "high",
        "observability_maturity": "full_tracing",
        "debugging_frequency": "continuous",
        "incident_mttr": "<30m",
    },
}

# === Drift cases gold labels ===
GOLD_DRIFT_CASES = [
    {
        "scenario": "kafka_alpha_to_nova",
        "decision_id": "DEC-ALPHA-001",
        "from_project": "alpha",
        "to_project": "nova",
        "expected_level": "high",
        "reconsideration_warranted": True,
        "changed_constraints": [
            "consumer_count",
            "replay_required",
            "traffic_volume",
            "ops_capacity",
            "async_workflows",
        ],
    },
    {
        "scenario": "redis_alpha_to_nova",
        "decision_id": "DEC-ALPHA-002",
        "from_project": "alpha",
        "to_project": "nova",
        "expected_level": "medium",
        "reconsideration_warranted": True,
        "changed_constraints": ["instance_count", "cache_hit_ratio", "session_persistence"],
    },
    {
        "scenario": "graphql_beta_to_nova",
        "decision_id": "DEC-BETA-001",
        "from_project": "beta",
        "to_project": "nova",
        "expected_level": "medium",
        "reconsideration_warranted": False,
        "changed_constraints": ["client_count", "client_diversity"],
        "note": "schema_complexity still high — key rejection reason unchanged",
    },
    {
        "scenario": "tracing_alpha_to_nova",
        "decision_id": "DEC-ALPHA-003",
        "from_project": "alpha",
        "to_project": "nova",
        "expected_level": "high",
        "reconsideration_warranted": True,
        "changed_constraints": ["observability_maturity", "debugging_frequency", "incident_mttr"],
    },
    {
        "scenario": "redis_gamma_to_nova",
        "decision_id": "DEC-GAMMA-001",
        "from_project": "gamma",
        "to_project": "nova",
        "expected_level": "low",
        "reconsideration_warranted": False,
        "changed_constraints": ["instance_count"],
        "note": "Same pattern, just more instances",
    },
]

# === Causal links gold labels ===
GOLD_CAUSAL_LINKS = [
    {
        "chain": "cedar",
        "decision_id": "DEC-DELTA-001",
        "from_step": "Backup removal decision",
        "to_step": "Database incident",
        "expected_label": "explicit_causal_link",
        "evidence": "SRC-DELTA-003 (postmortem explicitly names DEC-DELTA-001 as contributing factor)",
    },
    {
        "chain": "cedar",
        "decision_id": "DEC-DELTA-001",
        "from_step": "Cost optimization plan",
        "to_step": "Backup removal decision",
        "expected_label": "fact",
        "evidence": "SRC-DELTA-001 (cost plan documents the decision)",
    },
]

# === Evaluation questions ===
GOLD_EVAL_QUESTIONS = [
    {
        "question": "Why did Northstar reject Kafka in 2024?",
        "expected_decision_ids": ["DEC-ALPHA-001"],
        "expected_sources": ["SRC-ALPHA-001", "SRC-ALPHA-002"],
    },
    {
        "question": "Should Nova use Kafka for event streaming?",
        "expected_decision_ids": ["DEC-ALPHA-001"],
        "expected_drift": "high",
    },
    {
        "question": "What happened after removing backups?",
        "expected_decision_ids": ["DEC-DELTA-001"],
        "expected_sources": ["SRC-DELTA-003"],
    },
    {
        "question": "Has the Redis architecture changed over time?",
        "expected_decision_ids": ["DEC-ALPHA-002", "DEC-GAMMA-001"],
        "type": "pattern",
    },
    {
        "question": "Why was GraphQL rejected?",
        "expected_decision_ids": ["DEC-BETA-001"],
        "expected_sources": ["SRC-BETA-002"],
    },
    {
        "question": "Do the reasons for rejecting GraphQL still apply?",
        "expected_decision_ids": ["DEC-BETA-001"],
        "expected_drift": "medium",
    },
    {
        "question": "What is Northstar's approach to observability?",
        "expected_decision_ids": ["DEC-ALPHA-003"],
        "type": "pattern",
    },
    {
        "question": "Has the position on distributed tracing changed?",
        "expected_decision_ids": ["DEC-ALPHA-003"],
        "expected_drift": "high",
    },
    {
        "question": "What cost-cutting decisions were made in Delta?",
        "expected_decision_ids": ["DEC-DELTA-001"],
        "expected_sources": ["SRC-DELTA-001"],
    },
    {
        "question": "Were there any incidents linked to architectural decisions?",
        "expected_decision_ids": ["DEC-DELTA-001"],
        "type": "causal",
    },
    {
        "question": "How many consumers does Nova's event platform need?",
        "expected_decision_ids": ["DEC-ALPHA-001"],
        "expected_sources": ["SRC-NOVA-001", "SRC-NOVA-002"],
    },
    {
        "question": "What messaging system does Northstar currently use?",
        "expected_decision_ids": ["DEC-ALPHA-001"],
        "type": "current_state",
    },
    {
        "question": "Has Redis scaling been a recurring concern?",
        "expected_decision_ids": ["DEC-ALPHA-002", "DEC-GAMMA-001"],
        "type": "pattern",
    },
    {
        "question": "What lessons were learned from the database incident?",
        "expected_decision_ids": ["DEC-DELTA-001"],
        "expected_sources": ["SRC-DELTA-003"],
    },
    {
        "question": "Should Nova adopt GraphQL given the partner ecosystem?",
        "expected_decision_ids": ["DEC-BETA-001"],
        "expected_drift": "medium",
    },
]


def build_gold_labels(output_dir: str | Path) -> None:
    """Write all gold label files to the output directory."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    _write_json(output_dir / "decisions.json", GOLD_DECISIONS)
    _write_json(output_dir / "constraints.json", GOLD_CONSTRAINTS)
    _write_json(output_dir / "drift_cases.json", GOLD_DRIFT_CASES)
    _write_json(output_dir / "causal_links.json", GOLD_CAUSAL_LINKS)
    _write_json(output_dir / "eval_questions.json", GOLD_EVAL_QUESTIONS)


def _write_json(path: Path, data: object) -> None:
    """Write JSON data to file."""
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


if __name__ == "__main__":
    build_gold_labels(Path(__file__).parent.parent.parent / "data" / "gold")
    print("Gold labels written to data/gold/")
