"""Fixture builders — demo-quality data for all UI pages."""

from datetime import UTC, datetime

from contracts import (
    Alternative,
    AlternativeDisposition,
    BriefClaim,
    CausalLabel,
    CausalLink,
    ChainStep,
    Comparison,
    ConfidenceBreakdown,
    ConstraintDelta,
    ConstraintDeltaItem,
    CurrentProjectContext,
    Decision,
    DecisionBrief,
    DecisionStatus,
    DriftLevel,
    DriftResult,
    EpistemicType,
    EvidenceExcerpt,
    IngestResult,
    IngestStatus,
    MemoryOverview,
    MemoryTrace,
    MemoryTraceRecalled,
    MemoryTraceRetained,
    MentalModelView,
    ObservationHistory,
    ObservationView,
    OutcomeChain,
    ReviewQueueItem,
    TimelineEvent,
    TimelineEventKind,
)


def build_fixture_decision_alpha_kafka() -> Decision:
    """Alpha's Kafka rejection decision."""
    return Decision(
        decision_id="DEC-ALPHA-001",
        title="Reject Kafka for Event Streaming",
        statement="We will use RabbitMQ instead of Kafka because our ops team is small and we don't need replay capability.",
        date=datetime(2024, 5, 2, tzinfo=UTC),
        status=DecisionStatus.active,
        selected_option="RabbitMQ",
        reasons=["Complexity for 2 consumers", "No Kafka expertise", "Ops team too small"],
        constraints=[
            ConstraintDeltaItem(
                key="consumer_count",
                old_value=None,
                new_value="2",
                comparison=Comparison.changed,
                is_reason_linked=True,
                weight=0.8,
            ),
            ConstraintDeltaItem(
                key="ops_capacity",
                old_value=None,
                new_value="small",
                comparison=Comparison.changed,
                is_reason_linked=True,
                weight=0.9,
            ),
            ConstraintDeltaItem(
                key="replay_required",
                old_value=None,
                new_value="false",
                comparison=Comparison.changed,
                is_reason_linked=True,
                weight=0.7,
            ),
        ],
        alternatives=[
            Alternative(
                name="Kafka", disposition=AlternativeDisposition.rejected, reasons=["Too complex", "Ops overhead"]
            ),
            Alternative(
                name="RabbitMQ", disposition=AlternativeDisposition.selected, reasons=["Familiar", "Simple ops"]
            ),
            Alternative(name="SQS", disposition=AlternativeDisposition.deferred, reasons=["Vendor lock-in concern"]),
        ],
        technologies=["rabbitmq", "amqp"],
        source_ids=["SRC-ALPHA-001"],
        project_id="alpha",
    )


def build_fixture_decision_alpha_redis() -> Decision:
    """Alpha's Redis single-instance decision."""
    return Decision(
        decision_id="DEC-ALPHA-002",
        title="Use single-instance Redis for caching",
        statement="We will use a single Redis instance without clustering to reduce operational overhead.",
        date=datetime(2024, 6, 15, tzinfo=UTC),
        status=DecisionStatus.active,
        selected_option="Single Instance Redis",
        reasons=["Low instance count requirement", "High cache hit ratio achievable without cluster"],
        constraints=[],
        alternatives=[],
        technologies=["redis"],
        source_ids=["SRC-ALPHA-002"],
        project_id="alpha",
    )


def build_fixture_decision_alpha_tracing() -> Decision:
    """Alpha's structured logging decision."""
    return Decision(
        decision_id="DEC-ALPHA-003",
        title="Use structured logging instead of distributed tracing",
        statement="We will rely on structured logs rather than full distributed tracing.",
        date=datetime(2024, 7, 10, tzinfo=UTC),
        status=DecisionStatus.active,
        selected_option="Structured Logging",
        reasons=["Logs are sufficient for current scale", "Tracing adds too much overhead"],
        constraints=[],
        alternatives=[],
        technologies=["logging", "elk"],
        source_ids=["SRC-ALPHA-003"],
        project_id="alpha",
    )


def build_fixture_decision_beta_graphql() -> Decision:
    """Beta's GraphQL rejection."""
    return Decision(
        decision_id="DEC-BETA-001",
        title="Reject GraphQL for internal APIs",
        statement="We will stick with REST due to low client count and internal-only usage.",
        date=datetime(2025, 2, 20, tzinfo=UTC),
        status=DecisionStatus.active,
        selected_option="REST",
        reasons=["Schema complexity", "Internal only clients"],
        constraints=[],
        alternatives=[],
        technologies=["rest", "http"],
        source_ids=["SRC-BETA-001"],
        project_id="beta",
    )


def build_fixture_decision_gamma_redis() -> Decision:
    """Gamma's Redis cluster scaling."""
    return Decision(
        decision_id="DEC-GAMMA-001",
        title="Scale to Redis Cluster",
        statement="We will move from single-instance to a 4-node Redis cluster.",
        date=datetime(2025, 8, 5, tzinfo=UTC),
        status=DecisionStatus.active,
        selected_option="Redis Cluster",
        reasons=["Session persistence requires high availability"],
        constraints=[],
        alternatives=[],
        technologies=["redis", "clustering"],
        source_ids=["SRC-GAMMA-001"],
        project_id="gamma",
    )


def build_fixture_decision_delta_backup() -> Decision:
    """Delta's backup removal — the Cedar chain decision."""
    return Decision(
        decision_id="DEC-DELTA-001",
        title="Remove automated snapshot backups",
        statement="We will disable automated backups to save on cloud costs.",
        date=datetime(2025, 3, 15, tzinfo=UTC),
        status=DecisionStatus.active,
        selected_option="No Backups",
        reasons=["Budget pressure is high"],
        constraints=[],
        alternatives=[],
        technologies=["aws", "ebs"],
        source_ids=["SRC-DELTA-001"],
        project_id="delta",
        needs_review=False,
    )


def build_fixture_context_nova() -> CurrentProjectContext:
    """Nova's current project context."""
    return CurrentProjectContext(
        project_id="nova",
        project_name="Project Nova",
        constraints={
            "consumer_count": "15",
            "replay_required": "true",
            "traffic_volume": "high",
            "ops_capacity": "medium",
            "async_workflows": "true",
            "instance_count": "20",
            "cache_hit_ratio": "0.90",
            "session_persistence": "true",
            "client_count": "12",
            "client_diversity": "partner_ecosystem",
            "schema_complexity": "high",
            "observability_maturity": "full_tracing",
            "debugging_frequency": "continuous",
            "incident_mttr": "<30m",
        },
        updated_at=datetime.now(tz=UTC),
    )


def build_fixture_context_alpha() -> CurrentProjectContext:
    """Alpha's historical context (for reference)."""
    return CurrentProjectContext(
        project_id="alpha",
        project_name="Project Alpha",
        constraints={
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
        updated_at=datetime(2024, 9, 30, tzinfo=UTC),
    )


def build_fixture_context_beta() -> CurrentProjectContext:
    """Beta's historical context."""
    return CurrentProjectContext(
        project_id="beta",
        project_name="Project Beta",
        constraints={
            "client_count": "3",
            "client_diversity": "internal_only",
            "schema_complexity": "low",
            "consumer_count": "5",
            "async_workflows": "limited",
            "observability_maturity": "partial_tracing",
            "debugging_frequency": "daily",
            "incident_mttr": "2h",
        },
        updated_at=datetime(2025, 1, 31, tzinfo=UTC),
    )


def build_fixture_context_gamma() -> CurrentProjectContext:
    """Gamma's historical context."""
    return CurrentProjectContext(
        project_id="gamma",
        project_name="Project Gamma",
        constraints={
            "instance_count": "4",
            "cache_hit_ratio": "0.72",
            "session_persistence": "true",
        },
        updated_at=datetime(2025, 6, 30, tzinfo=UTC),
    )


def build_fixture_context_delta() -> CurrentProjectContext:
    """Delta's historical context (confidential cost optimization)."""
    return CurrentProjectContext(
        project_id="delta",
        project_name="Project Delta (Confidential)",
        constraints={
            "backup_policy": "none",
            "budget_pressure": "high",
            "data_criticality": "medium",
        },
        updated_at=datetime(2025, 9, 30, tzinfo=UTC),
    )


def build_fixture_drift_alpha_nova() -> DriftResult:
    """Kafka drift: Alpha→Nova = HIGH."""
    return DriftResult(
        decision_id="DEC-ALPHA-001",
        level=DriftLevel.high,
        score=0.92,
        delta=ConstraintDelta(
            items=[
                ConstraintDeltaItem(
                    key="consumer_count",
                    old_value="2",
                    new_value="15",
                    comparison=Comparison.changed,
                    is_reason_linked=True,
                    weight=1.0,
                ),
                ConstraintDeltaItem(
                    key="ops_capacity",
                    old_value="small",
                    new_value="medium",
                    comparison=Comparison.changed,
                    is_reason_linked=True,
                    weight=0.8,
                ),
                ConstraintDeltaItem(
                    key="replay_required",
                    old_value="false",
                    new_value="true",
                    comparison=Comparison.changed,
                    is_reason_linked=True,
                    weight=0.9,
                ),
                ConstraintDeltaItem(
                    key="traffic_volume",
                    old_value="moderate",
                    new_value="high",
                    comparison=Comparison.changed,
                    is_reason_linked=False,
                    weight=0.5,
                ),
                ConstraintDeltaItem(
                    key="async_workflows",
                    old_value="false",
                    new_value="true",
                    comparison=Comparison.changed,
                    is_reason_linked=False,
                    weight=0.6,
                ),
            ]
        ),
        reconsideration_warranted=True,
        summary="All original constraints that drove the Kafka rejection have significantly changed. Consumer count is up 7.5x, ops capacity has improved, and replay is now required.",
    )


def build_fixture_drift_redis() -> DriftResult:
    """Redis drift: Alpha→Nova = MEDIUM."""
    return DriftResult(
        decision_id="DEC-ALPHA-002",
        level=DriftLevel.medium,
        score=0.55,
        delta=ConstraintDelta(items=[]),
        reconsideration_warranted=False,
        summary="Redis usage has scaled, but core principles might still apply.",
    )


def build_fixture_drift_graphql() -> DriftResult:
    """GraphQL drift: Beta→Nova = MEDIUM but reconsideration NOT warranted."""
    return DriftResult(
        decision_id="DEC-BETA-001",
        level=DriftLevel.medium,
        score=0.48,
        delta=ConstraintDelta(items=[]),
        reconsideration_warranted=False,
        summary="Client diversity changed, but schema complexity remains high, blocking reconsideration.",
    )


def build_fixture_drift_tracing() -> DriftResult:
    """Tracing drift: Alpha→Nova = HIGH."""
    return DriftResult(
        decision_id="DEC-ALPHA-003",
        level=DriftLevel.high,
        score=0.88,
        delta=ConstraintDelta(items=[]),
        reconsideration_warranted=True,
        summary="Observability maturity needs have outgrown structured logging.",
    )


def build_fixture_brief_nova_kafka() -> DecisionBrief:
    """The demo brief: 'Should Nova use Kafka?'"""
    nova_ctx = build_fixture_context_nova()
    return DecisionBrief(
        query_id="q-nova-kafka-001",
        question="Should Nova use Kafka for event streaming?",
        project_id="nova",
        current_constraints=nova_ctx.constraints,
        historical_decision=build_fixture_decision_alpha_kafka(),
        drift=build_fixture_drift_alpha_nova(),
        claims=[
            BriefClaim(
                text="Kafka provides the necessary replay capabilities required by Nova.",
                epistemic_type=EpistemicType.fact,
                source_ids=["SRC-NOVA-001"],
            ),
            BriefClaim(
                text="Ops capacity has grown from small to medium, mitigating earlier maintenance concerns.",
                epistemic_type=EpistemicType.observation,
                source_ids=["SRC-ALPHA-001", "SRC-NOVA-002"],
            ),
            BriefClaim(
                text="RabbitMQ struggles with the current consumer count of 15.",
                epistemic_type=EpistemicType.inference,
                source_ids=["SRC-BETA-001"],
            ),
            BriefClaim(
                text="Migrate event streaming to Kafka to support async workflows natively.",
                epistemic_type=EpistemicType.recommendation,
                source_ids=["SRC-NOVA-001", "SRC-NOVA-002"],
            ),
        ],
        confidence=ConfidenceBreakdown(
            evidence_quality=0.85, temporal_relevance=0.70, source_agreement=0.90, information_completeness=0.75
        ),
        source_ids=["SRC-ALPHA-001", "SRC-ALPHA-002", "SRC-ALPHA-003", "SRC-BETA-001", "SRC-NOVA-001", "SRC-NOVA-002"],
    )


def build_fixture_outcome_chain_cedar() -> OutcomeChain:
    """Cedar chain: backup removal → incident → postmortem."""
    return OutcomeChain(
        chain_id="chain-cedar-001",
        decision_id="DEC-DELTA-001",
        steps=[
            ChainStep(
                step_id="step-1",
                title="Decision: Remove Automated Backups",
                date=datetime(2025, 3, 15, tzinfo=UTC),
                source_ids=["SRC-DELTA-001"],
            ),
            ChainStep(
                step_id="step-2",
                title="Implementation: Automated Backups Disabled",
                date=datetime(2025, 4, 15, tzinfo=UTC),
                source_ids=["SRC-DELTA-002"],
            ),
            ChainStep(
                step_id="step-3",
                title="Outage Event: Production Database Corruption",
                date=datetime(2025, 7, 22, tzinfo=UTC),
                source_ids=["SRC-DELTA-003"],
            ),
            ChainStep(
                step_id="step-4",
                title="Postmortem: Direct Root-Cause Attribution",
                date=datetime(2025, 8, 1, tzinfo=UTC),
                source_ids=["SRC-DELTA-003"],
            ),
            ChainStep(
                step_id="step-5",
                title="Consequence: Backups Restored & Policy Hardened",
                date=datetime(2025, 8, 15, tzinfo=UTC),
                source_ids=["SRC-DELTA-004"],
            ),
        ],
        links=[
            CausalLink(
                label=CausalLabel.fact,
                rationale="Implementation completed per cost optimization directive.",
                evidence_ids=["SRC-DELTA-002"],
            ),
            CausalLink(
                label=CausalLabel.strong_evidence,
                rationale="Outage recovery delayed due to lack of point-in-time restore capability.",
                evidence_ids=["SRC-DELTA-003"],
            ),
            CausalLink(
                label=CausalLabel.explicit_causal_link,
                rationale="Postmortem explicitly names removal of automated backups (DEC-DELTA-001) as direct contributing factor.",
                evidence_ids=["SRC-DELTA-003"],
            ),
            CausalLink(
                label=CausalLabel.fact,
                rationale="Engineering leadership allocated dedicated budget to restore daily automated backups.",
                evidence_ids=["SRC-DELTA-004"],
            ),
        ],
    )


def build_fixture_timeline_kafka() -> list[TimelineEvent]:
    """Kafka decision timeline from Alpha through Nova."""
    return [
        TimelineEvent(
            event_id="te-1",
            decision_id="DEC-ALPHA-001",
            kind=TimelineEventKind.original_decision,
            title="Kafka Rejected",
            occurred_at=datetime(2024, 5, 2, tzinfo=UTC),
            status=DecisionStatus.active,
            summary="Original decision to use RabbitMQ.",
        ),
        TimelineEvent(
            event_id="te-2",
            decision_id="DEC-ALPHA-001",
            kind=TimelineEventKind.exception,
            title="Beta Workaround",
            occurred_at=datetime(2024, 11, 20, tzinfo=UTC),
            status=DecisionStatus.active,
            summary="Beta project creates a custom replay queue on top of RabbitMQ.",
        ),
        TimelineEvent(
            event_id="te-3",
            decision_id="DEC-ALPHA-001",
            kind=TimelineEventKind.reconsideration,
            title="Nova Revisit",
            occurred_at=datetime(2026, 2, 3, tzinfo=UTC),
            status=DecisionStatus.reconsidered,
            summary="Nova team initiates a formal reconsideration due to high drift.",
        ),
    ]


def build_fixture_timeline_cedar() -> list[TimelineEvent]:
    """Cedar timeline: decision → outcome → incident."""
    return [
        TimelineEvent(
            event_id="te-c1",
            decision_id="DEC-DELTA-001",
            kind=TimelineEventKind.original_decision,
            title="Backups Removed",
            occurred_at=datetime(2025, 3, 15, tzinfo=UTC),
            summary="Cost-cutting measure.",
        ),
        TimelineEvent(
            event_id="te-c2",
            decision_id="DEC-DELTA-001",
            kind=TimelineEventKind.outcome,
            title="Incident",
            occurred_at=datetime(2025, 7, 22, tzinfo=UTC),
            summary="Critical data loss.",
        ),
        TimelineEvent(
            event_id="te-c3",
            decision_id="DEC-DELTA-001",
            kind=TimelineEventKind.supersession,
            title="Backups Restored",
            occurred_at=datetime(2025, 8, 15, tzinfo=UTC),
            summary="Decision reversed.",
        ),
    ]


def build_fixture_evidence_map() -> dict[str, EvidenceExcerpt]:
    """Map of source_id → evidence excerpts for the evidence panel."""
    return {
        "SRC-ALPHA-001": EvidenceExcerpt(
            source_id="SRC-ALPHA-001",
            excerpt="We only have 2 engineers with ops experience, Kafka is too heavy.",
            date=datetime(2024, 5, 1, tzinfo=UTC),
            project_id="alpha",
            kind=EpistemicType.fact,
        ),
        "SRC-ALPHA-002": EvidenceExcerpt(
            source_id="SRC-ALPHA-002",
            excerpt="Single instance Redis is enough for our 85% cache hit ratio.",
            date=datetime(2024, 6, 10, tzinfo=UTC),
            project_id="alpha",
            kind=EpistemicType.fact,
        ),
        "SRC-ALPHA-003": EvidenceExcerpt(
            source_id="SRC-ALPHA-003",
            excerpt="Let's stick to ELK for now.",
            date=datetime(2024, 7, 5, tzinfo=UTC),
            project_id="alpha",
            kind=EpistemicType.fact,
        ),
        "SRC-BETA-001": EvidenceExcerpt(
            source_id="SRC-BETA-001",
            excerpt="GraphQL schema overhead isn't worth it for 3 internal clients.",
            date=datetime(2025, 2, 18, tzinfo=UTC),
            project_id="beta",
            kind=EpistemicType.fact,
        ),
        "SRC-NOVA-001": EvidenceExcerpt(
            source_id="SRC-NOVA-001",
            excerpt="We need strong replayability for the new event-driven architecture.",
            date=datetime(2026, 1, 15, tzinfo=UTC),
            project_id="nova",
            kind=EpistemicType.fact,
        ),
        "SRC-NOVA-002": EvidenceExcerpt(
            source_id="SRC-NOVA-002",
            excerpt="Ops capacity has grown; we now have a dedicated platform team.",
            date=datetime(2026, 1, 20, tzinfo=UTC),
            project_id="nova",
            kind=EpistemicType.observation,
        ),
        "SRC-DELTA-001": EvidenceExcerpt(
            source_id="SRC-DELTA-001",
            excerpt="Budget pressure requires cutting non-essential AWS costs immediately.",
            date=datetime(2025, 3, 10, tzinfo=UTC),
            project_id="delta",
            kind=EpistemicType.fact,
        ),
        "SRC-DELTA-002": EvidenceExcerpt(
            source_id="SRC-DELTA-002",
            excerpt="Disabled automated RDS snapshots.",
            date=datetime(2025, 4, 15, tzinfo=UTC),
            project_id="delta",
            kind=EpistemicType.fact,
        ),
        "SRC-DELTA-003": EvidenceExcerpt(
            source_id="SRC-DELTA-003",
            excerpt="Incident report: table truncated, no backup available for point-in-time recovery.",
            date=datetime(2025, 7, 22, tzinfo=UTC),
            project_id="delta",
            kind=EpistemicType.observation,
        ),
        "SRC-DELTA-004": EvidenceExcerpt(
            source_id="SRC-DELTA-004",
            excerpt="Postmortem explicitly names removal of automated backups as direct contributing factor.",
            date=datetime(2025, 8, 1, tzinfo=UTC),
            project_id="delta",
            kind=EpistemicType.inference,
        ),
    }


def build_fixture_memory_overview() -> MemoryOverview:
    """Overview stats for the opening screen."""
    return MemoryOverview(
        project_count=5,
        source_count=18,
        decision_count=6,
        fact_count=42,
        observation_count=12,
        mental_model_count=3,
        last_updated=datetime.now(tz=UTC),
    )


def build_fixture_observations() -> list[ObservationView]:
    """Observations for Memory Evolution page."""
    return [
        ObservationView(
            observation_id="obs-1",
            statement="Async messaging needs grow with consumer count",
            evidence_count=5,
            supporting_source_ids=["SRC-ALPHA-001", "SRC-NOVA-001"],
            first_seen=datetime(2024, 6, 1, tzinfo=UTC),
            last_updated=datetime.now(tz=UTC),
            history=[
                ObservationHistory(
                    timestamp=datetime(2024, 6, 1, tzinfo=UTC), evidence_count=1, summary="Initial thought."
                )
            ],
        ),
        ObservationView(
            observation_id="obs-2",
            statement="Cost-cutting without risk assessment leads to incidents",
            evidence_count=8,
            supporting_source_ids=["SRC-DELTA-004"],
            first_seen=datetime(2025, 8, 1, tzinfo=UTC),
            last_updated=datetime.now(tz=UTC),
            history=[],
        ),
        ObservationView(
            observation_id="obs-3",
            statement="Redis scaling follows predictable patterns",
            evidence_count=4,
            supporting_source_ids=["SRC-ALPHA-002", "SRC-GAMMA-001"],
            first_seen=datetime(2024, 6, 15, tzinfo=UTC),
            last_updated=datetime.now(tz=UTC),
            history=[],
        ),
        ObservationView(
            observation_id="obs-4",
            statement="Debugging complexity grows faster than service count",
            evidence_count=6,
            supporting_source_ids=["SRC-ALPHA-003"],
            first_seen=datetime(2024, 7, 10, tzinfo=UTC),
            last_updated=datetime.now(tz=UTC),
            history=[],
        ),
    ]


def build_fixture_mental_models() -> list[MentalModelView]:
    """Mental models for Memory Evolution page."""
    return [
        MentalModelView(
            model_id="mm-1",
            name="Organizational Readiness",
            content="Technology adoption follows organizational readiness.",
            evidence_count=12,
            last_refreshed=datetime.now(tz=UTC),
        ),
        MentalModelView(
            model_id="mm-2",
            name="Risk Quantification",
            content="Cost optimization decisions require explicit risk quantification.",
            evidence_count=8,
            last_refreshed=datetime.now(tz=UTC),
        ),
        MentalModelView(
            model_id="mm-3",
            name="Observability Maturity",
            content="Observability maturity must scale with system complexity.",
            evidence_count=10,
            last_refreshed=datetime.now(tz=UTC),
        ),
    ]


def build_fixture_memory_trace_kafka() -> MemoryTrace:
    """Memory trace for the Kafka query."""
    return MemoryTrace(
        query_id="q-nova-kafka-001",
        retained=[
            MemoryTraceRetained(source_id="SRC-ALPHA-001", title="ADR: Reject Kafka"),
            MemoryTraceRetained(source_id="SRC-NOVA-001", title="Nova Requirements Doc"),
        ],
        recalled=[
            MemoryTraceRecalled(
                memory_id="mem-1", kind="Concept", relevance=0.95, entities=["Kafka", "RabbitMQ", "Event Streaming"]
            ),
        ],
        observations_used=["obs-1"],
    )


def build_fixture_review_queue() -> list[ReviewQueueItem]:
    """Items needing review for the Explorer review tab."""
    return [
        ReviewQueueItem(
            decision_id="DEC-BETA-001",
            title="Reject GraphQL for internal APIs",
            reason="Drift detected but reconsideration flag is ambiguous.",
            confidence=ConfidenceBreakdown(
                evidence_quality=0.6, temporal_relevance=0.8, source_agreement=0.5, information_completeness=0.4
            ),
        ),
        ReviewQueueItem(
            decision_id="DEC-ALPHA-003",
            title="Use structured logging instead of distributed tracing",
            reason="High temporal distance since original decision.",
            confidence=ConfidenceBreakdown(
                evidence_quality=0.7, temporal_relevance=0.3, source_agreement=0.8, information_completeness=0.6
            ),
        ),
    ]


def build_fixture_ingest_result_nova() -> IngestResult:
    """Fixture ingest result for demo."""
    return IngestResult(
        status=IngestStatus.success,
        source_id="SRC-NOVA-003",
        memories_created=8,
        decisions_extracted=0,
        outcomes_linked=2,
        needs_review_ids=[],
        warnings=[],
    )


def build_fixture_brief_graphql_alpha_partner() -> DecisionBrief:
    """GraphQL drift but still rejected — proves drift != forced reversal."""
    return DecisionBrief(
        query_id="q-graphql-alpha-partner",
        question="Why was GraphQL rejected for internal APIs?",
        project_id="nova",
        current_constraints={
            "client_count": "12",
            "client_diversity": "partner_ecosystem",
            "schema_complexity": "high",
        },
        historical_decision=build_fixture_decision_beta_graphql(),
        drift=build_fixture_drift_graphql(),
        claims=[
            BriefClaim(
                text="Client count increased from 3 to 12.",
                epistemic_type=EpistemicType.fact,
                source_ids=["SRC-BETA-002"],
            ),
            BriefClaim(
                text="Schema complexity remains too high to justify migration.",
                epistemic_type=EpistemicType.observation,
                source_ids=["SRC-BETA-002"],
            ),
        ],
        confidence=ConfidenceBreakdown(
            evidence_quality=0.80, temporal_relevance=0.65, source_agreement=0.85, information_completeness=0.70
        ),
        source_ids=["SRC-BETA-002"],
    )


def build_fixture_brief_redis_scale() -> DecisionBrief:
    """Redis scaling story — straightforward drift."""
    return DecisionBrief(
        query_id="q-redis-scale",
        question="Has our Redis position changed?",
        project_id="nova",
        current_constraints={"instance_count": "20", "cache_hit_ratio": "0.90", "session_persistence": "true"},
        historical_decision=build_fixture_decision_alpha_redis(),
        drift=build_fixture_drift_redis(),
        claims=[
            BriefClaim(
                text="Instance count scaled significantly.",
                epistemic_type=EpistemicType.fact,
                source_ids=["SRC-ALPHA-004"],
            ),
            BriefClaim(
                text="Single instance is showing degradation under load.",
                epistemic_type=EpistemicType.observation,
                source_ids=["SRC-GAMMA-001"],
            ),
        ],
        confidence=ConfidenceBreakdown(
            evidence_quality=0.85, temporal_relevance=0.75, source_agreement=0.90, information_completeness=0.80
        ),
        source_ids=["SRC-ALPHA-004", "SRC-GAMMA-001"],
    )


def build_fixture_brief_cedar_outcome() -> DecisionBrief:
    """Cedar backup removal — the causal chain story."""
    return DecisionBrief(
        query_id="q-cedar-outcome",
        question="What happened after Cedar skipped backups?",
        project_id="delta",
        current_constraints={"backup_policy": "daily_incremental", "data_criticality": "high"},
        historical_decision=build_fixture_decision_delta_backup(),
        drift=None,
        claims=[
            BriefClaim(
                text="Automated backups were disabled to save costs.",
                epistemic_type=EpistemicType.fact,
                source_ids=["SRC-DELTA-001"],
            ),
            BriefClaim(
                text="A critical data loss incident occurred.",
                epistemic_type=EpistemicType.observation,
                source_ids=["SRC-DELTA-002"],
            ),
            BriefClaim(
                text="Postmortem explicitly names removal of automated backups as direct contributing factor.",
                epistemic_type=EpistemicType.inference,
                source_ids=["SRC-DELTA-003"],
            ),
            BriefClaim(
                text="Maintain daily incremental backups for all high-criticality data.",
                epistemic_type=EpistemicType.recommendation,
                source_ids=["SRC-DELTA-003"],
            ),
        ],
        confidence=ConfidenceBreakdown(
            evidence_quality=0.90, temporal_relevance=0.85, source_agreement=0.95, information_completeness=0.88
        ),
        source_ids=["SRC-DELTA-001", "SRC-DELTA-002", "SRC-DELTA-003"],
    )


def build_all_fixture_decisions() -> list[Decision]:
    """All 6 decisions for search/explorer."""
    return [
        build_fixture_decision_alpha_kafka(),
        build_fixture_decision_alpha_redis(),
        build_fixture_decision_alpha_tracing(),
        build_fixture_decision_beta_graphql(),
        build_fixture_decision_gamma_redis(),
        build_fixture_decision_delta_backup(),
    ]


def build_all_fixture_projects() -> list[CurrentProjectContext]:
    """All projects for the project list."""
    return [
        build_fixture_context_nova(),
        build_fixture_context_alpha(),
        build_fixture_context_beta(),
        build_fixture_context_gamma(),
        build_fixture_context_delta(),
    ]
