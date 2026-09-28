from enum import Enum


class DecisionStatus(str, Enum):
    active = "active"
    reconsidered = "reconsidered"
    superseded = "superseded"
    exception = "exception"


class AlternativeDisposition(str, Enum):
    selected = "selected"
    rejected = "rejected"
    deferred = "deferred"


class AssumptionStatus(str, Enum):
    active = "active"
    invalidated = "invalidated"


class MemoryKind(str, Enum):
    world = "world"
    experience = "experience"
    observation = "observation"


class ConstraintComparison(str, Enum):
    SAME = "same"
    CHANGED = "changed"
    UNKNOWN = "unknown"
    INCOMPARABLE = "incomparable"
    NEWLY_PRESENT = "newly_present"


class DriftLevel(str, Enum):
    none = "none"
    low = "low"
    medium = "medium"
    high = "high"
    NONE = "NONE"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class EpistemicType(str, Enum):
    fact = "fact"
    observation = "observation"
    inference = "inference"
    recommendation = "recommendation"


class EpistemicLabel(str, Enum):
    FACT = "FACT"
    OBSERVATION = "OBSERVATION"
    INFERENCE = "INFERENCE"
    RECOMMENDATION = "RECOMMENDATION"


class CausalLabel(str, Enum):
    explicit_causal_link = "explicit_causal_link"
    strong_evidence = "strong_evidence"
    possible_causal_link = "possible_causal_link"
    fact = "fact"
    none = "none"
    NONE = "none"
    POSSIBLE_CAUSAL_LINK = "possible_causal_link"
    STRONG_EVIDENCE = "strong_evidence"
    EXPLICIT_CAUSAL_LINK = "explicit_causal_link"


class Comparison(str, Enum):
    same = "same"
    changed = "changed"
    newly_present = "newly_present"
    unknown = "unknown"
    incomparable = "incomparable"


class Role(str, Enum):
    ENGINEER = "engineer"
    ARCHITECT = "architect"
    MANAGER = "manager"


class SourceType(str, Enum):
    architecture_doc = "architecture_doc"
    adr = "adr"
    meeting_notes = "meeting_notes"
    email = "email"
    design_doc = "design_doc"
    meeting_transcript = "meeting_transcript"
    postmortem = "postmortem"
    retro = "retro"
    implementation_note = "implementation_note"


class TimelineEventKind(str, Enum):
    original_decision = "original_decision"
    exception = "exception"
    outcome = "outcome"
    reconsideration = "reconsideration"
    supersession = "supersession"


class IngestStatus(str, Enum):
    success = "success"
    partial = "partial"
    failed = "failed"
