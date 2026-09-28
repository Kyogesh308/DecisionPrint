from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from .enums import (
    AlternativeDisposition,
    CausalLabel,
    Comparison,
    DecisionStatus,
    DriftLevel,
    EpistemicType,
    IngestStatus,
    SourceType,
    TimelineEventKind,
)


class SourceManifestEntry(BaseModel):
    """Manifest entry for a document source."""

    source_id: str
    project_id: str
    source_type: SourceType
    title: str
    file_path: str
    date: datetime
    tags: list[str] = []
    sensitivity: str = "internal"
    is_current: bool = False


class ConstraintDeltaItem(BaseModel):
    """Represents a delta in a specific constraint."""

    key: str
    old_value: str | None = None
    new_value: str | None = None
    comparison: Comparison
    is_reason_linked: bool = False
    weight: float = 0.0


class ConstraintDelta(BaseModel):
    """Collection of constraint changes."""

    items: list[ConstraintDeltaItem]


class BriefClaim(BaseModel):
    """A brief epistemic claim."""

    text: str
    epistemic_type: EpistemicType
    source_ids: list[str] = []


class ConfidenceBreakdown(BaseModel):
    """Breakdown of confidence scores."""

    evidence_quality: float | None = None
    temporal_relevance: float | None = None
    source_agreement: float | None = None
    information_completeness: float | None = None


class Alternative(BaseModel):
    """An alternative option considered during a decision."""

    name: str
    disposition: AlternativeDisposition
    reasons: list[str] = []


class Decision(BaseModel):
    """Represents an architectural decision."""

    decision_id: str
    title: str
    statement: str
    date: datetime
    status: DecisionStatus
    selected_option: str
    reasons: list[str] = []
    constraints: list[ConstraintDeltaItem] = []
    alternatives: list[Alternative] = []
    technologies: list[str] = []
    source_ids: list[str] = []
    project_id: str
    needs_review: bool = False


class DriftResult(BaseModel):
    """Result of analyzing architectural drift."""

    decision_id: str
    level: DriftLevel
    score: float
    delta: ConstraintDelta
    reconsideration_warranted: bool = False
    summary: str = ""


class DecisionBrief(BaseModel):
    """Brief representation of a decision in response to a query."""

    query_id: str
    question: str
    project_id: str
    current_constraints: dict[str, str] = {}
    historical_decision: Decision | None = None
    drift: DriftResult | None = None
    claims: list[BriefClaim] = []
    confidence: ConfidenceBreakdown | None = None
    source_ids: list[str] = []


class EvidenceExcerpt(BaseModel):
    """An excerpt from a source used as evidence."""

    source_id: str
    excerpt: str
    date: datetime | None = None
    project_id: str = ""
    kind: EpistemicType = EpistemicType.fact


class TimelineEvent(BaseModel):
    """An event on the decision timeline."""

    event_id: str
    decision_id: str
    kind: TimelineEventKind
    title: str
    occurred_at: datetime
    status: DecisionStatus = DecisionStatus.active
    summary: str = ""


class MemoryOverview(BaseModel):
    """High-level overview of memory backend state."""

    project_count: int = 0
    source_count: int = 0
    decision_count: int = 0
    fact_count: int = 0
    observation_count: int = 0
    mental_model_count: int = 0
    last_updated: datetime | None = None


class CurrentProjectContext(BaseModel):
    """Current contextual constraints and metadata for a project."""

    project_id: str
    project_name: str
    constraints: dict[str, str] = {}
    updated_at: datetime | None = None


class IngestResult(BaseModel):
    """Result of source ingestion."""

    status: IngestStatus
    source_id: str
    memories_created: int = 0
    decisions_extracted: int = 0
    outcomes_linked: int = 0
    needs_review_ids: list[str] = []
    warnings: list[str] = []


class CausalLink(BaseModel):
    """A causal link in an outcome chain."""

    label: CausalLabel
    rationale: str = ""
    evidence_ids: list[str] = []


class ChainStep(BaseModel):
    """A single step in a decision's outcome chain."""

    step_id: str
    title: str
    date: datetime | None = None
    source_ids: list[str] = []


class OutcomeChain(BaseModel):
    """A chain of events linking a decision to its outcomes."""

    chain_id: str
    decision_id: str
    steps: list[ChainStep] = []
    links: list[CausalLink] = []


class ObservationHistory(BaseModel):
    """Historical context for an observation."""

    timestamp: datetime
    evidence_count: int
    summary: str = ""


class ObservationView(BaseModel):
    """Current view of a deduced observation."""

    observation_id: str
    statement: str
    evidence_count: int = 0
    supporting_source_ids: list[str] = []
    first_seen: datetime | None = None
    last_updated: datetime | None = None
    history: list[ObservationHistory] = []


class MentalModelView(BaseModel):
    """A high-level mental model aggregated from observations."""

    model_id: str
    name: str
    content: str
    last_refreshed: datetime | None = None
    evidence_count: int = 0


class MemoryTraceRetained(BaseModel):
    """Represents a direct memory that was retained."""

    source_id: str
    title: str = ""


class MemoryTraceRecalled(BaseModel):
    """Represents a synthetic memory that was recalled."""

    memory_id: str
    kind: str = ""
    relevance: float = 0.0
    entities: list[str] = []


class MemoryTrace(BaseModel):
    """The trace of memories accessed for a given query."""

    query_id: str
    retained: list[MemoryTraceRetained] = []
    recalled: list[MemoryTraceRecalled] = []
    observations_used: list[str] = []


class DecisionFilter(BaseModel):
    """Criteria for searching decisions."""

    text: str | None = None
    project_id: str | None = None
    technology: str | None = None
    status: DecisionStatus | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None


class ReviewQueueItem(BaseModel):
    """Item needing human review."""

    decision_id: str
    title: str
    reason: str = ""
    confidence: ConfidenceBreakdown | None = None
