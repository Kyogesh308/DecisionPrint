from enum import Enum

class DecisionStatus(Enum):
    active = "active"
    reconsidered = "reconsidered"
    superseded = "superseded"
    exception = "exception"

class AlternativeDisposition(Enum):
    selected = "selected"
    rejected = "rejected"
    deferred = "deferred"

class AssumptionStatus(Enum):
    active = "active"
    invalidated = "invalidated"

class MemoryKind(Enum):
    world = "world"
    experience = "experience"
    observation = "observation"

class ConstraintComparison(Enum):
    SAME = "same"
    CHANGED = "changed"
    UNKNOWN = "unknown"
    INCOMPARABLE = "incomparable"
    NEWLY_PRESENT = "newly_present"

class DriftLevel(Enum):
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class EpistemicLabel(Enum):
    FACT = "FACT"
    OBSERVATION = "OBSERVATION"
    INFERENCE = "INFERENCE"
    RECOMMENDATION = "RECOMMENDATION"

class Role(Enum):
    ENGINEER = "engineer"
    ARCHITECT = "architect"
    MANAGER = "manager"

class SourceType(Enum):
    architecture_doc = "architecture_doc"
    meeting_notes = "meeting_notes"
    email = "email"
    design_doc = "design_doc"
    meeting_transcript = "meeting_transcript"
    postmortem = "postmortem"

class CausalLabel(Enum):
    NONE = "none"
    POSSIBLE_CAUSAL_LINK = "possible_causal_link"
    STRONG_EVIDENCE = "strong_evidence"
    EXPLICIT_CAUSAL_LINK = "explicit_causal_link"
