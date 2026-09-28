from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, model_validator

from .enums import (
    AlternativeDisposition,
    AssumptionStatus,
    CausalLabel,
    Comparison,
    ConstraintComparison,
    DecisionStatus,
    DriftLevel,
    EpistemicLabel,
    EpistemicType,
    IngestStatus,
    MemoryKind,
    Role,
    SourceType,
    TimelineEventKind,
)


class SourceRef(BaseModel):
    source_id: str
    document_id: str | None = None
    chunk_id: str | None = None
    locator: str | None = None
    excerpt: str | None = None


class Constraint(BaseModel):
    key: str
    value: Any
    unit: str | None = None
    normalized_value: Any | None = None
    source_memory_id: str | None = None
    is_reason_linked: bool = False


class Assumption(BaseModel):
    statement: str
    status: AssumptionStatus | str = AssumptionStatus.active
    source_memory_id: str | None = None


class Alternative(BaseModel):
    name: str | None = None
    option: str | None = None
    disposition: AlternativeDisposition
    reason: str | None = None
    reasons: list[str] = Field(default_factory=list)
    source_memory_id: str | None = None

    @model_validator(mode="before")
    @classmethod
    def _normalize_option_name(cls, values: Any) -> Any:
        if isinstance(values, dict):
            values = values.copy()
            values.setdefault("name", values.get("option"))
            values.setdefault("option", values.get("name"))
        return values


class Reason(BaseModel):
    statement: str
    source_memory_id: str | None = None


class ConstraintDeltaItem(BaseModel):
    key: str
    old_value: Any | None = None
    new_value: Any | None = None
    historical_value: Any | None = None
    current_value: Any | None = None
    comparison: Comparison | ConstraintComparison
    is_reason_linked: bool = False
    weight: float = 0.0
    note: str | None = None


class ConstraintDelta(BaseModel):
    decision_id: str | None = None
    project_id: str | None = None
    items: list[ConstraintDeltaItem] = Field(default_factory=list)


class Decision(BaseModel):
    decision_id: str | None = None
    id: str | None = None
    title: str
    statement: str | None = None
    decision_statement: str | None = None
    date: datetime | None = None
    occurred_at: datetime | None = None
    status: DecisionStatus
    selected_option: str | None = None
    reasons: list[str | Reason] = Field(default_factory=list)
    constraints: list[Constraint | ConstraintDeltaItem] = Field(default_factory=list)
    assumptions: list[Assumption] = Field(default_factory=list)
    alternatives: list[Alternative] = Field(default_factory=list)
    technologies: list[str] = Field(default_factory=list)
    source_ids: list[str] = Field(default_factory=list)
    source_refs: list[SourceRef] = Field(default_factory=list)
    project_id: str
    participants: list[str] = Field(default_factory=list)
    context_summary: str = ""
    extraction_confidence: float = 0.0
    outcome_refs: list[str] = Field(default_factory=list)
    superseded_by: str | None = None
    related_decisions: list[str] = Field(default_factory=list)
    needs_review: bool = False

    @model_validator(mode="before")
    @classmethod
    def _normalize_branch_fields(cls, values: Any) -> Any:
        if not isinstance(values, dict):
            return values
        values = values.copy()
        for left, right in (
            ("id", "decision_id"),
            ("statement", "decision_statement"),
            ("date", "occurred_at"),
        ):
            if left not in values and right in values:
                values[left] = values[right]
            if right not in values and left in values:
                values[right] = values[left]
        return values


class CurrentProjectContext(BaseModel):
    project_id: str
    summary: str | None = None
    project_name: str | None = None
    constraints: list[Constraint] | dict[str, str] = Field(default_factory=list)
    source_refs: list[SourceRef] = Field(default_factory=list)
    updated_at: datetime | None = None


class RecalledMemory(BaseModel):
    memory_id: str
    kind: MemoryKind
    text: str
    summary: str | None = None
    occurred_at: datetime | None = None
    entities: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    source_refs: list[SourceRef] = Field(default_factory=list)
    relevance: float = 0.0


class RecallBundle(BaseModel):
    query: str
    memories: list[RecalledMemory] = Field(default_factory=list)
    decision_ids: list[str] = Field(default_factory=list)
    retrieval_confidence: float = 0.0


class DriftResult(BaseModel):
    decision_id: str
    level: DriftLevel
    score: float
    delta: ConstraintDelta
    reconsideration_warranted: bool = False
    drift_confidence: float | None = None
    summary: str = ""


class BriefClaim(BaseModel):
    text: str
    epistemic_type: EpistemicType | None = None
    label: EpistemicLabel | None = None
    source_ids: list[str] = Field(default_factory=list)
    memory_ids: list[str] = Field(default_factory=list)
    source_refs: list[SourceRef] = Field(default_factory=list)


class ConfidenceBreakdown(BaseModel):
    evidence_quality: float | None = None
    temporal_relevance: float | None = None
    source_agreement: float | None = None
    information_completeness: float | None = None
    extraction: float | None = None
    retrieval: float | None = None
    drift: float | None = None
    causal: float | None = None


class DecisionBrief(BaseModel):
    query_id: str
    query: str | None = None
    question: str | None = None
    project_id: str
    answer_summary: str = ""
    current_constraints: list[Constraint] | dict[str, str] = Field(default_factory=list)
    historical_decision: Decision | None = None
    historical_decisions: list[BriefClaim] = Field(default_factory=list)
    historical_constraints: list[Constraint] = Field(default_factory=list)
    constraint_differences: list[ConstraintDelta] = Field(default_factory=list)
    claims: list[BriefClaim] = Field(default_factory=list)
    observations: list[BriefClaim] = Field(default_factory=list)
    inferences: list[BriefClaim] = Field(default_factory=list)
    drift: DriftResult | None = None
    reconsideration_warranted: bool = False
    recommendation: BriefClaim | None = None
    confidence: ConfidenceBreakdown | None = None
    sources: list[SourceRef] = Field(default_factory=list)
    source_ids: list[str] = Field(default_factory=list)
    generated_at: str = ""

    @model_validator(mode="before")
    @classmethod
    def _normalize_question_query(cls, values: Any) -> Any:
        if isinstance(values, dict):
            values = values.copy()
            values.setdefault("query", values.get("question"))
            values.setdefault("question", values.get("query"))
        return values


class SourceManifestEntry(BaseModel):
    """Manifest entry for a document source from either branch contract."""

    source_id: str
    project_id: str
    source_type: SourceType
    title: str
    file_path: str | None = None
    path: str | None = None
    date: datetime | None = None
    occurred_at: datetime | None = None
    tags: list[str] = Field(default_factory=list)
    sensitivity: str = "internal"
    is_current: bool = False

    @model_validator(mode="before")
    @classmethod
    def _normalize_path_and_date(cls, values: Any) -> Any:
        if not isinstance(values, dict):
            return values
        values = values.copy()
        for left, right in (("file_path", "path"), ("date", "occurred_at")):
            if left not in values and right in values:
                values[left] = values[right]
            if right not in values and left in values:
                values[right] = values[left]
        return values


class EvidenceExcerpt(BaseModel):
    source_id: str
    excerpt: str
    date: datetime | None = None
    project_id: str = ""
    kind: EpistemicType = EpistemicType.fact


class TimelineEvent(BaseModel):
    event_id: str
    decision_id: str
    kind: TimelineEventKind
    title: str
    occurred_at: datetime
    status: DecisionStatus = DecisionStatus.active
    summary: str = ""


class MemoryOverview(BaseModel):
    project_count: int = 0
    source_count: int = 0
    decision_count: int = 0
    fact_count: int = 0
    observation_count: int = 0
    mental_model_count: int = 0
    last_updated: datetime | None = None


class IngestResult(BaseModel):
    status: IngestStatus
    source_id: str
    memories_created: int = 0
    decisions_extracted: int = 0
    outcomes_linked: int = 0
    needs_review_ids: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class CausalLink(BaseModel):
    decision_id: str | None = None
    outcome_id: str | None = None
    label: CausalLabel
    rationale: str = ""
    evidence_ids: list[str] = Field(default_factory=list)
    confidence: float | None = None


class ChainStep(BaseModel):
    step_id: str
    title: str
    date: datetime | None = None
    source_ids: list[str] = Field(default_factory=list)


class OutcomeChain(BaseModel):
    chain_id: str
    decision_id: str
    steps: list[ChainStep] = Field(default_factory=list)
    links: list[CausalLink] = Field(default_factory=list)


class ObservationHistory(BaseModel):
    timestamp: datetime
    evidence_count: int
    summary: str = ""


class ObservationView(BaseModel):
    observation_id: str
    statement: str
    evidence_count: int = 0
    supporting_source_ids: list[str] = Field(default_factory=list)
    first_seen: datetime | None = None
    last_updated: datetime | None = None
    history: list[ObservationHistory] = Field(default_factory=list)


class MentalModelView(BaseModel):
    model_id: str
    name: str
    content: str
    last_refreshed: datetime | None = None
    evidence_count: int = 0


class MemoryTraceRetained(BaseModel):
    source_id: str
    title: str = ""


class MemoryTraceRecalled(BaseModel):
    memory_id: str
    kind: str = ""
    relevance: float = 0.0
    entities: list[str] = Field(default_factory=list)


class MemoryTrace(BaseModel):
    query_id: str
    retained: list[MemoryTraceRetained] = Field(default_factory=list)
    recalled: list[MemoryTraceRecalled] = Field(default_factory=list)
    observations_used: list[str] = Field(default_factory=list)


class DecisionFilter(BaseModel):
    text: str | None = None
    project_id: str | None = None
    technology: str | None = None
    status: DecisionStatus | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None


class ReviewQueueItem(BaseModel):
    decision_id: str
    title: str
    reason: str = ""
    confidence: ConfidenceBreakdown | None = None


class ReflectResult(BaseModel):
    text: str
    memory_ids: list[str] = Field(default_factory=list)
    source_refs: list[SourceRef] = Field(default_factory=list)


class Scope(BaseModel):
    role: Role
    allowed_project_ids: list[str] = Field(default_factory=list)
    allowed_tags: list[str] = Field(default_factory=list)
    visibility_levels: list[str] = Field(default_factory=list)


class RetainResult(BaseModel):
    source_id: str
    document_id: str
    memory_ids: list[str] = Field(default_factory=list)
    memories: list[RecalledMemory] = Field(default_factory=list)


class Outcome(BaseModel):
    outcome_id: str
    project_id: str
    occurred_at: datetime
    statement: str
    source_refs: list[SourceRef] = Field(default_factory=list)
    decision_ids: list[str] = Field(default_factory=list)
    causal_label: CausalLabel
    confidence: float


ProjectContext = CurrentProjectContext