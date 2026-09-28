"""Live backend — thin pass-through to the facade module."""

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
        return self._facade.update_project_context(context, user_role)

    def ingest_source(self, entry: SourceManifestEntry, content: str, user_role: str) -> IngestResult:
        return self._facade.ingest_source(entry, content, user_role)

    def search_decisions(self, filter: DecisionFilter, user_role: str) -> list[Decision]:
        return self._facade.search_decisions(filter, user_role)

    def get_decision(self, decision_id: str, user_role: str) -> Decision:
        return self._facade.get_decision(decision_id, user_role)

    def get_decision_timeline(self, decision_id: str, user_role: str) -> list[TimelineEvent]:
        return self._facade.get_decision_timeline(decision_id, user_role)

    def ask_question(self, question: str, project_id: str, user_role: str) -> DecisionBrief:
        return self._facade.ask_question(question, project_id, user_role)

    def list_drift_cards(self, project_id: str, user_role: str) -> list[DriftResult]:
        return self._facade.list_drift_cards(project_id, user_role)

    def get_evidence(self, source_id: str, user_role: str) -> EvidenceExcerpt:
        return self._facade.get_evidence(source_id, user_role)

    def get_outcome_chain(self, decision_id: str, user_role: str) -> OutcomeChain:
        return self._facade.get_outcome_chain(decision_id, user_role)

    def list_observations(self, user_role: str, topic: str | None = None) -> list[ObservationView]:
        return self._facade.list_observations(user_role, topic)

    def list_mental_models(self, user_role: str) -> list[MentalModelView]:
        return self._facade.list_mental_models(user_role)

    def get_memory_trace(self, query_id: str, user_role: str) -> MemoryTrace:
        return self._facade.get_memory_trace(query_id, user_role)

    def list_review_queue(self, user_role: str) -> list[ReviewQueueItem]:
        return self._facade.list_review_queue(user_role)
