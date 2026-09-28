"""Live backend — thin pass-through to the facade module."""

from contracts.enums import EpistemicType, IngestStatus
from contracts import (
    CurrentProjectContext,
    Decision,
    DecisionBrief,
    DecisionFilter,
    DriftResult,
    EvidenceExcerpt,
    IngestResult,
    MemoryOverview,
    MemoryTrace,
    MentalModelView,
    ObservationView,
    OutcomeChain,
    ReviewQueueItem,
    SourceManifestEntry,
    TimelineEvent,
)
from contracts.models import BriefClaim, ConfidenceBreakdown, SourceRef


class LiveBackend:
    """Passes all calls to the real facade (P1's code)."""

    def __init__(self) -> None:
        """Lazy import facade to avoid import errors when facade isn't available."""
        try:
            import facade

            self._facade = facade
        except ImportError as e:
            from contracts.errors import MemoryUnavailableError

            raise MemoryUnavailableError("Facade module not available. Is P1's code merged?") from e

    def get_memory_overview(self, user_role: str) -> MemoryOverview:
        return self._facade.get_memory_overview(user_role)

    def list_projects(self, user_role: str) -> list[CurrentProjectContext]:
        return self._facade.list_projects(user_role)

    def get_project_context(self, project_id: str, user_role: str) -> CurrentProjectContext:
        return self._facade.get_project_context(project_id, user_role)

    def update_project_context(self, context: CurrentProjectContext, user_role: str) -> CurrentProjectContext:
        self._facade.get_project_context(context.project_id, user_role)
        if isinstance(context.constraints, dict):
            values = dict(context.constraints)
        else:
            values = {constraint.key: constraint.value for constraint in context.constraints}
        consumer_count = values.get("consumer_count")
        replay_required = values.get("replay_required")
        self._facade.update_project_context(
            context.project_id,
            consumer_count=consumer_count if isinstance(consumer_count, int) else None,
            replay_required=replay_required if isinstance(replay_required, bool) else None,
            context_json=values,
        )
        return self._facade.get_project_context(context.project_id, user_role)

    def ingest_source(self, entry: SourceManifestEntry, content: str, user_role: str) -> IngestResult:
        result = self._facade.ingest_source(user_role, entry.model_dump(mode="json"), content)
        return IngestResult(
            status=IngestStatus.success if result.get("status") == "stored" else IngestStatus.failed,
            source_id=result["source_id"],
            memories_created=len(result.get("memory_ids", [])),
            warnings=result.get("warnings", []),
        )

    def search_decisions(self, filter: DecisionFilter, user_role: str) -> list[Decision]:
        return self._facade.search_decisions(filter, user_role)

    def get_decision(self, decision_id: str, user_role: str) -> Decision:
        return self._facade.get_decision(decision_id, user_role)

    def get_decision_timeline(self, decision_id: str, user_role: str) -> list[TimelineEvent]:
        return self._facade.get_decision_timeline(decision_id, user_role)

    def ask_question(self, question: str, project_id: str, user_role: str) -> DecisionBrief:
        result = self._facade.ask_question(user_role, project_id, question)
        answer = result.get("answer", "")
        source_ids = result.get("source_ids", [])
        claims = (
            [BriefClaim(text=answer, epistemic_type=EpistemicType.fact, source_ids=source_ids)]
            if answer
            else []
        )
        return DecisionBrief(
            query_id=result["query_id"],
            question=question,
            project_id=project_id,
            answer_summary=answer,
            claims=claims,
            sources=[SourceRef(source_id=source_id) for source_id in source_ids],
            source_ids=source_ids,
            confidence=ConfidenceBreakdown(retrieval=result.get("retrieval_confidence", 0.0)),
        )

    def list_drift_cards(self, project_id: str, user_role: str) -> list[DriftResult]:
        return self._facade.list_drift_cards(user_role, project_id)

    def get_evidence(self, source_id: str, user_role: str) -> EvidenceExcerpt:
        return self._facade.get_evidence(source_id, user_role)

    def get_outcome_chain(self, decision_id: str, user_role: str) -> OutcomeChain:
        return OutcomeChain.model_validate(self._facade.get_outcome_chain(user_role, decision_id))

    def list_observations(self, user_role: str, topic: str | None = None) -> list[ObservationView]:
        return self._facade.list_observations(user_role, topic)

    def list_mental_models(self, user_role: str) -> list[MentalModelView]:
        return self._facade.list_mental_models(user_role)

    def get_memory_trace(self, query_id: str, user_role: str) -> MemoryTrace:
        return self._facade.get_memory_trace(query_id, user_role)

    def list_review_queue(self, user_role: str) -> list[ReviewQueueItem]:
        return self._facade.list_review_queue(user_role)
