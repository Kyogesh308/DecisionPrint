from enum import Enum


class DriftLevel(str, Enum):
    none = "none"
    low = "low"
    medium = "medium"
    high = "high"


class EpistemicType(str, Enum):
    fact = "fact"
    observation = "observation"
    inference = "inference"
    recommendation = "recommendation"


class CausalLabel(str, Enum):
    explicit_causal_link = "explicit_causal_link"
    strong_evidence = "strong_evidence"
    possible_causal_link = "possible_causal_link"
    fact = "fact"
    none = "none"


class Comparison(str, Enum):
    same = "same"
    changed = "changed"
    newly_present = "newly_present"
    unknown = "unknown"
    incomparable = "incomparable"


class DecisionStatus(str, Enum):
    active = "active"
    superseded = "superseded"
    reconsidered = "reconsidered"


class SourceType(str, Enum):
    architecture_doc = "architecture_doc"
    adr = "adr"
    meeting_transcript = "meeting_transcript"
    retro = "retro"
    postmortem = "postmortem"
    implementation_note = "implementation_note"
    design_doc = "design_doc"


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


class AlternativeDisposition(str, Enum):
    selected = "selected"
    rejected = "rejected"
    deferred = "deferred"
