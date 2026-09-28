"""Fixture backend for UI demo."""

from __future__ import annotations

from pathlib import Path

from contracts import (
    CurrentProjectContext,
    Decision,
    DecisionBrief,
    DecisionFilter,
    DriftResult,
    EpistemicType,
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
from contracts.errors import NotFoundError, ScopeError
from ui.fixtures import builders


class FixtureBackend:
    """Provides demo-quality fixture data."""

    def __init__(self) -> None:
        self._overview = builders.build_fixture_memory_overview()
        self._projects = {p.project_id: p for p in builders.build_all_fixture_projects()}
        self._decisions = {d.decision_id: d for d in builders.build_all_fixture_decisions()}
        self._evidence = builders.build_fixture_evidence_map()

    def _check_scope(self, project_id: str, user_role: str) -> None:
        """Enforce role-based access control rules."""
        if user_role == "engineer" and project_id.lower() == "delta":
            raise ScopeError(
                "Access Denied: Project 'delta' is marked confidential (infrastructure cost cuts). "
                "The 'engineer' role is not permitted to view confidential records. "
                "Switch to 'executive' or 'admin' in the sidebar to review this project."
            )

    def get_memory_overview(self, user_role: str) -> MemoryOverview:
        """Return high-level memory statistics."""
        return self._overview

    def list_projects(self, user_role: str) -> list[CurrentProjectContext]:
        """List active and historical projects visible to user role."""
        if user_role == "engineer":
            return [p for p in self._projects.values() if p.project_id != "delta"]
        return list(self._projects.values())

    def get_project_context(self, project_id: str, user_role: str) -> CurrentProjectContext:
        """Get contextual metadata and constraints for a project."""
        self._check_scope(project_id, user_role)
        pid = project_id.lower()
        if pid not in self._projects:
            raise NotFoundError(f"Project '{project_id}' not found in organizational memory.")
        return self._projects[pid]

    def update_project_context(self, context: CurrentProjectContext, user_role: str) -> CurrentProjectContext:
        """Update context constraints for an active project."""
        self._check_scope(context.project_id, user_role)
        self._projects[context.project_id.lower()] = context
        return context

    def ingest_source(self, entry: SourceManifestEntry, content: str, user_role: str) -> IngestResult:
        """Simulate ingesting a new document into memory and updating counters."""
        self._check_scope(entry.project_id, user_role)
        res = builders.build_fixture_ingest_result_nova()
        res.source_id = entry.source_id

        # Update in-memory counts so the 'Memory updated' moment is visibly reflected
        self._overview.source_count += 1
        self._overview.fact_count += res.memories_created

        # Store excerpt in evidence map
        lines = [line.strip() for line in content.splitlines() if line.strip() and not line.startswith("#")]
        excerpt = lines[0] if lines else content[:250]
        self._evidence[entry.source_id] = EvidenceExcerpt(
            source_id=entry.source_id,
            excerpt=excerpt,
            date=entry.date,
            project_id=entry.project_id,
            kind=EpistemicType.fact,
        )
        return res

    def search_decisions(self, filter: DecisionFilter, user_role: str) -> list[Decision]:
        """Search and filter decisions by text, project, technology, or status."""
        results = list(self._decisions.values())
        if user_role == "engineer":
            results = [d for d in results if d.project_id != "delta"]

        if filter.project_id:
            results = [d for d in results if d.project_id.lower() == filter.project_id.lower()]
        if filter.status:
            results = [d for d in results if d.status == filter.status]
        if filter.technology:
            tech_q = filter.technology.lower()
            results = [d for d in results if any(tech_q in t.lower() for t in d.technologies)]
        if filter.text:
            txt = filter.text.lower()
            results = [
                d
                for d in results
                if txt in d.title.lower()
                or txt in d.statement.lower()
                or txt in d.selected_option.lower()
                or any(txt in t.lower() for t in d.technologies)
                or any(txt in r.lower() for r in d.reasons)
            ]
        return results

    def get_decision(self, decision_id: str, user_role: str) -> Decision:
        """Fetch a single decision by its ID."""
        did = decision_id.upper()
        if did not in self._decisions:
            raise NotFoundError(f"Decision '{decision_id}' not found.")
        dec = self._decisions[did]
        self._check_scope(dec.project_id, user_role)
        return dec

    def get_decision_timeline(self, decision_id: str, user_role: str) -> list[TimelineEvent]:
        """Get the chronological evolution timeline for a decision."""
        did = decision_id.upper()
        if did == "DEC-DELTA-001":
            self._check_scope("delta", user_role)
            return builders.build_fixture_timeline_cedar()
        return builders.build_fixture_timeline_kafka()

    def ask_question(self, question: str, project_id: str, user_role: str) -> DecisionBrief:
        """The core organizational memory question answering endpoint."""
        self._check_scope(project_id, user_role)
        q = question.lower()
        if "graphql" in q:
            return builders.build_fixture_brief_graphql_alpha_partner()
        if "redis" in q:
            return builders.build_fixture_brief_redis_scale()
        if "cedar" in q or "backup" in q:
            return builders.build_fixture_brief_cedar_outcome()
        if "kafka" in q or project_id.lower() == "nova":
            return builders.build_fixture_brief_nova_kafka()

        # Sensible brief for other queries
        return DecisionBrief(
            query_id="q-query-general",
            question=question,
            project_id=project_id,
            claims=[],
            source_ids=[],
        )

    def list_drift_cards(self, project_id: str, user_role: str) -> list[DriftResult]:
        """List active drift cards for a project."""
        self._check_scope(project_id, user_role)
        pid = project_id.lower()
        if pid == "nova":
            return [
                builders.build_fixture_drift_alpha_nova(),
                builders.build_fixture_drift_redis(),
                builders.build_fixture_drift_graphql(),
                builders.build_fixture_drift_tracing(),
            ]
        elif pid == "alpha":
            return [builders.build_fixture_drift_alpha_nova()]
        return []

    def get_evidence(self, source_id: str, user_role: str) -> EvidenceExcerpt:
        """Fetch primary evidence excerpt for a source ID."""
        sid = source_id.upper()
        if sid.startswith("SRC-DELTA") and user_role == "engineer":
            raise ScopeError(f"Access denied to evidence {source_id} for role '{user_role}'.")

        if sid in self._evidence:
            return self._evidence[sid]

        # Scan local markdown files in data directory as fallback
        base_dir = Path(__file__).resolve().parent.parent.parent
        data_dir = base_dir / "data"
        for md_file in data_dir.glob(f"**/*{sid}*.md"):
            content = md_file.read_text(encoding="utf-8")
            lines = [
                line.strip()
                for line in content.splitlines()
                if line.strip() and not line.startswith("#") and not line.startswith("**")
            ]
            excerpt = lines[0] if lines else content[:250]
            proj = sid.split("-")[1].lower() if "-" in sid else ""
            return EvidenceExcerpt(
                source_id=sid,
                excerpt=excerpt,
                project_id=proj,
                kind=EpistemicType.fact,
            )

        raise NotFoundError(f"Evidence source '{source_id}' not found.")

    def get_outcome_chain(self, decision_id: str, user_role: str) -> OutcomeChain:
        """Retrieve causal chain of outcomes following a decision."""
        did = decision_id.upper()
        if did == "DEC-DELTA-001":
            self._check_scope("delta", user_role)
            return builders.build_fixture_outcome_chain_cedar()

        return OutcomeChain(
            chain_id="chain-kafka-001",
            decision_id=did,
            steps=[
                builders.ChainStep(
                    step_id="step-1", title="Alpha Reject Kafka (RabbitMQ Selected)", source_ids=["SRC-ALPHA-001"]
                ),
                builders.ChainStep(step_id="step-2", title="Beta Workaround Queue", source_ids=["SRC-BETA-001"]),
                builders.ChainStep(step_id="step-3", title="Nova Scale Reaches Limit", source_ids=["SRC-NOVA-001"]),
            ],
            links=[
                builders.CausalLink(
                    label=builders.CausalLabel.strong_evidence,
                    rationale="Consumer scale outgrew RabbitMQ cluster throughput limits.",
                    evidence_ids=["SRC-BETA-001", "SRC-NOVA-001"],
                ),
            ],
        )

    def list_observations(self, user_role: str, topic: str | None = None) -> list[ObservationView]:
        """List synthesized organizational observations."""
        obs = builders.build_fixture_observations()
        if topic:
            t = topic.lower()
            return [o for o in obs if t in o.statement.lower()]
        return obs

    def list_mental_models(self, user_role: str) -> list[MentalModelView]:
        """List higher-order mental models."""
        return builders.build_fixture_mental_models()

    def get_memory_trace(self, query_id: str, user_role: str) -> MemoryTrace:
        """Audit trail showing memories retrieved and active during query synthesis."""
        if query_id == "q-nova-kafka-001" or "kafka" in query_id.lower():
            return builders.build_fixture_memory_trace_kafka()
        return MemoryTrace(
            query_id=query_id,
            retained=[builders.MemoryTraceRetained(source_id="SRC-ALPHA-001", title="Platform v2 Architecture")],
            recalled=[
                builders.MemoryTraceRecalled(
                    memory_id="mem-01", kind="Fact", relevance=0.88, entities=["RabbitMQ", "Kafka"]
                )
            ],
            observations_used=["Technology adoption follows organizational readiness."],
        )

    def list_review_queue(self, user_role: str) -> list[ReviewQueueItem]:
        """List low-confidence extractions flagged for human review."""
        return builders.build_fixture_review_queue()
