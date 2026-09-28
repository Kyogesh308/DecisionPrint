from typing import List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from .enums import DecisionStatus, AlternativeDisposition, AssumptionStatus, MemoryKind, ConstraintComparison, DriftLevel, EpistemicLabel, Role, SourceType, CausalLabel

class SourceRef(BaseModel):
    source_id: str
    document_id: Optional[str] = None
    chunk_id: Optional[str] = None
    locator: Optional[str] = None
    excerpt: Optional[str] = None

class Constraint(BaseModel):
    key: str
    value: Any
    unit: Optional[str] = None
    normalized_value: Optional[Any] = None
    source_memory_id: Optional[str] = None
    is_reason_linked: bool = False

class Assumption(BaseModel):
    statement: str
    status: str
    source_memory_id: Optional[str] = None

class Alternative(BaseModel):
    option: str
    disposition: str
    reason: Optional[str] = None
    source_memory_id: Optional[str] = None

class Reason(BaseModel):
    statement: str
    source_memory_id: Optional[str] = None

class Decision(BaseModel):
    model_config = ConfigDict(use_enum_values=True)
    id: str
    project_id: str
    title: str
    decision_statement: str
    occurred_at: datetime
    participants: List[str]
    context_summary: str
    constraints: List[Constraint]
    assumptions: List[Assumption]
    alternatives: List[Alternative]
    selected_option: str
    reasons: List[Reason]
    technologies: List[str]
    source_refs: List[SourceRef]
    extraction_confidence: float
    outcome_refs: List[str]
    status: DecisionStatus
    superseded_by: Optional[str] = None
    related_decisions: List[str]
    needs_review: bool

class CurrentProjectContext(BaseModel):
    project_id: str
    summary: str
    constraints: List[Constraint]
    source_refs: List[SourceRef]
    updated_at: datetime

class RecalledMemory(BaseModel):
    model_config = ConfigDict(use_enum_values=True)
    memory_id: str
    kind: MemoryKind
    text: str
    occurred_at: Optional[datetime] = None
    entities: List[str]
    tags: List[str]
    source_refs: List[SourceRef]
    relevance: float

class RecallBundle(BaseModel):
    query: str
    memories: List[RecalledMemory]
    decision_ids: List[str]
    retrieval_confidence: float

class ConstraintDeltaItem(BaseModel):
    key: str
    historical_value: Optional[Any] = None
    current_value: Optional[Any] = None
    comparison: ConstraintComparison
    is_reason_linked: bool
    weight: float
    note: Optional[str] = None

class ConstraintDelta(BaseModel):
    decision_id: str
    project_id: str
    items: List[ConstraintDeltaItem]

class DriftResult(BaseModel):
    model_config = ConfigDict(use_enum_values=False)
    decision_id: str
    score: float
    level: DriftLevel
    reconsideration_warranted: bool
    drift_confidence: float
    delta: ConstraintDelta

class BriefClaim(BaseModel):
    text: str
    label: EpistemicLabel
    memory_ids: List[str]
    source_refs: List[SourceRef]

class ConfidenceBreakdown(BaseModel):
    extraction: Optional[float] = None
    retrieval: Optional[float] = None
    drift: Optional[float] = None
    causal: Optional[float] = None

class DecisionBrief(BaseModel):
    query_id: str
    query: str
    project_id: str
    answer_summary: str
    historical_decisions: List[BriefClaim]
    historical_constraints: List[Constraint]
    current_constraints: List[Constraint]
    constraint_differences: List[ConstraintDelta]
    observations: List[BriefClaim]
    inferences: List[BriefClaim]
    drift: Optional[DriftResult] = None
    reconsideration_warranted: bool
    recommendation: BriefClaim
    confidence: ConfidenceBreakdown
    sources: List[SourceRef]
    generated_at: str

class ReflectResult(BaseModel):
    text: str
    memory_ids: List[str]
    source_refs: List[SourceRef]

class Scope(BaseModel):
    role: Role
    allowed_project_ids: List[str]
    allowed_tags: List[str]
    visibility_levels: List[str]

class SourceManifestEntry(BaseModel):
    source_id: str
    project_id: str
    source_type: SourceType
    title: str
    occurred_at: Optional[datetime] = None
    path: str
    sensitivity: str
    tags: List[str]
    is_current: bool

class RetainResult(BaseModel):
    source_id: str
    document_id: str
    memory_ids: List[str]
    memories: List[RecalledMemory]

class Outcome(BaseModel):
    outcome_id: str
    project_id: str
    occurred_at: datetime
    statement: str
    source_refs: List[SourceRef]
    decision_ids: List[str]
    causal_label: CausalLabel
    confidence: float

class CausalLink(BaseModel):
    decision_id: str
    outcome_id: str
    label: CausalLabel
    rationale: str
    evidence_ids: List[str]
    confidence: float
