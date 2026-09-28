from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from contracts.enums import CausalLabel, DecisionStatus, EpistemicType, TimelineEventKind
from contracts.errors import NotFoundError
from contracts.models import (
    Constraint,
    CurrentProjectContext,
    CausalLink,
    ChainStep,
    Decision,
    DecisionFilter,
    EvidenceExcerpt,
    MemoryOverview,
    MemoryTrace,
    MemoryTraceRecalled,
    MentalModelView,
    OutcomeChain,
    ObservationView,
    SourceRef,
    TimelineEvent,
)
from intelligence.drift import compare_constraints, score_drift
from memory import (
    MemoryUnavailableError,
    list_mental_models as read_mental_models,
    recall_memories,
    reflect_on_question,
    retain_source,
)
from store import (
    ScopeError,
    assert_project_allowed,
    get_project,
    get_decision_record,
    get_project_context_record,
    get_source,
    init_database,
    list_audit_events,
    list_causal_link_records,
    list_decision_records,
    list_outcome_records,
    list_project_records,
    list_projects_in_scope,
    list_source_records,
    record_audit_event,
    resolve_scope,
    save_project_context,
    save_source,
    upsert_project,
    get_project,
    list_projects_in_scope,
)


def _ensure_initialized() -> None:
    init_database()


def ingest_source(user_role: str, entry: dict[str, Any], text: str) -> dict[str, Any]:
    """Persist a source, retain its text in Hindsight, and store the decision context."""
    _ensure_initialized()
    scope = resolve_scope(user_role)
    project_id = str(entry["project_id"])
    assert_project_allowed(scope, project_id)

    source_id = str(entry.get("source_id") or f"source-{project_id}-{len(list_audit_events()) + 1}")
    source_type = entry.get("source_type", "general")
    title = entry.get("title")
    upsert_project(project_id, project_id.replace("-", " ").title())
    save_source(
        source_id,
        project_id,
        source_type=source_type,
        hindsight_document_id=source_id,
        title=title,
    )

    retain_result = retain_source(source_id, text, tags=["decision", "technology"], metadata={"project_id": project_id})
    if entry.get("is_current"):
        update_project_context(project_id, context_json={"last_source_id": source_id})

    record_audit_event(
        action="ingest_source",
        role=user_role,
        project_id=project_id,
        query_id=f"ingest-{source_id}",
        decision_ids=[],
        output_hash=None,
        recalled_memory_ids=retain_result.memory_ids,
        scope=scope,
        actor=user_role,
    )

    return {
        "source_id": source_id,
        "project_id": project_id,
        "source_type": source_type,
        "memory_ids": retain_result.memory_ids,
        "status": "stored",
    }


def update_project_context(project_id: str, *, consumer_count: int | None = None, replay_required: bool | None = None, context_json: dict[str, Any] | None = None) -> dict[str, Any]:
    """Update the current project context used for drift comparisons."""
    _ensure_initialized()
    payload = context_json or {}
    if consumer_count is not None:
        payload["consumer_count"] = consumer_count
    if replay_required is not None:
        payload["replay_required"] = replay_required
    return save_project_context(
        project_id,
        consumer_count=consumer_count,
        replay_required=replay_required,
        context_json=payload,
    )


def _as_datetime(value: Any, *, fallback: datetime | None = None) -> datetime:
    if isinstance(value, datetime):
        return value
    if value:
        try:
            parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
            return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)
        except ValueError:
            pass
    return fallback or datetime.now(UTC)


def _decision_from_record(record: dict[str, Any]) -> Decision:
    status = record.get("status") or DecisionStatus.active.value
    try:
        decision_status = DecisionStatus(status)
    except ValueError:
        decision_status = DecisionStatus.active
    decision_id = str(record["decision_id"])
    source_ids = [
        source["source_id"]
        for source in list_source_records(project_id=record["project_id"])
        if source["source_id"] == decision_id
    ]
    occurred_at = _as_datetime(record.get("occurred_at") or record.get("created_at"))
    return Decision(
        decision_id=decision_id,
        title=record.get("title") or decision_id,
        statement=record.get("decision_statement") or "",
        date=occurred_at,
        status=decision_status,
        project_id=record["project_id"],
        selected_option="",
        source_ids=source_ids,
        source_refs=[SourceRef(source_id=source_id) for source_id in source_ids],
        superseded_by=record.get("superseded_by"),
    )


def get_memory_overview(user_role: str) -> MemoryOverview:
    _ensure_initialized()
    scope = resolve_scope(user_role)
    project_ids = list_projects_in_scope(scope)
    visible_sources = [
        source
        for source in list_source_records()
        if source["project_id"] in project_ids
    ]
    visible_decisions = [
        decision
        for decision in list_decision_records()
        if decision["project_id"] in project_ids
    ]
    last_updated = max(
        (_as_datetime(source["created_at"]) for source in visible_sources),
        default=None,
    )
    return MemoryOverview(
        project_count=len(project_ids),
        source_count=len(visible_sources),
        decision_count=len(visible_decisions),
        fact_count=0,
        observation_count=0,
        mental_model_count=0,
        last_updated=last_updated,
    )


def list_projects(user_role: str) -> list[CurrentProjectContext]:
    _ensure_initialized()
    scope = resolve_scope(user_role)
    return [
        get_project_context(record["project_id"], user_role)
        for record in list_project_records(scope)
    ]


def get_project_context(project_id: str, user_role: str) -> CurrentProjectContext:
    _ensure_initialized()
    scope = resolve_scope(user_role)
    assert_project_allowed(scope, project_id)
    try:
        project = get_project(project_id)
    except KeyError as exc:
        raise NotFoundError(f"Project '{project_id}' was not found") from exc
    try:
        stored = get_project_context_record(project_id)
    except KeyError:
        stored = {}
    values = dict(stored.get("context_json") or {})
    for key in ("consumer_count", "replay_required"):
        if stored.get(key) is not None:
            values[key] = stored[key]
    constraints = {str(key): str(value) for key, value in values.items()}
    return CurrentProjectContext(
        project_id=project_id,
        project_name=project.get("name"),
        summary=project.get("description"),
        constraints=constraints,
        updated_at=_as_datetime(stored.get("updated_at"), fallback=None) if stored else None,
    )


def search_decisions(filter: DecisionFilter, user_role: str) -> list[Decision]:
    _ensure_initialized()
    scope = resolve_scope(user_role)
    decisions: list[Decision] = []
    for record in list_decision_records(project_id=filter.project_id):
        try:
            assert_project_allowed(scope, record["project_id"])
        except ScopeError:
            continue
        decision = _decision_from_record(record)
        text = filter.text.casefold() if filter.text else None
        if text and text not in f"{decision.title} {decision.statement}".casefold():
            continue
        if filter.technology and filter.technology.casefold() not in decision.statement.casefold():
            continue
        if filter.status and decision.status != filter.status:
            continue
        if filter.date_from and decision.date and decision.date < filter.date_from:
            continue
        if filter.date_to and decision.date and decision.date > filter.date_to:
            continue
        decisions.append(decision)
    return decisions


def get_decision(decision_id: str, user_role: str) -> Decision:
    _ensure_initialized()
    try:
        record = get_decision_record(decision_id)
    except KeyError as exc:
        raise NotFoundError(f"Decision '{decision_id}' was not found") from exc
    assert_project_allowed(resolve_scope(user_role), record["project_id"])
    return _decision_from_record(record)


def get_decision_timeline(decision_id: str, user_role: str) -> list[TimelineEvent]:
    decision = get_decision(decision_id, user_role)
    record = get_decision_record(decision_id)
    events = [
        TimelineEvent(
            event_id=f"{decision_id}:decision",
            decision_id=decision_id,
            kind=TimelineEventKind.original_decision,
            title=decision.title,
            occurred_at=decision.date or _as_datetime(record.get("created_at")),
            status=decision.status,
            summary=decision.statement or "",
        )
    ]
    for outcome in list_outcome_records(decision_id=decision_id):
        events.append(
            TimelineEvent(
                event_id=str(outcome["outcome_id"]),
                decision_id=decision_id,
                kind=TimelineEventKind.outcome,
                title=outcome.get("title") or "Outcome",
                occurred_at=_as_datetime(outcome.get("created_at")),
                status=decision.status,
                summary=outcome.get("summary") or "",
            )
        )
    return sorted(events, key=lambda event: event.occurred_at)


def get_evidence(source_id: str, user_role: str) -> EvidenceExcerpt:
    _ensure_initialized()
    try:
        source = get_source(source_id)
    except KeyError as exc:
        raise NotFoundError(f"Evidence source '{source_id}' was not found") from exc
    scope = resolve_scope(user_role)
    assert_project_allowed(scope, source["project_id"])

    excerpt = ""
    data_dir = Path(__file__).resolve().parent.parent / "data"
    for path in data_dir.glob(f"**/*{source_id}*.md"):
        content = path.read_text(encoding="utf-8")
        excerpt = next(
            (line.strip() for line in content.splitlines() if line.strip() and not line.lstrip().startswith("#")),
            "",
        )
        if excerpt:
            break
    if not excerpt:
        recalled = recall_memories(source_id, scope, limit=1).results
        excerpt = next((item.text for item in recalled if item.source_id == source_id), "")
    if not excerpt:
        raise NotFoundError(f"No retained excerpt found for source '{source_id}'")
    return EvidenceExcerpt(
        source_id=source_id,
        excerpt=excerpt,
        date=_as_datetime(source["created_at"]),
        project_id=source["project_id"],
        kind=EpistemicType.fact,
    )


def list_observations(user_role: str, topic: str | None = None) -> list[ObservationView]:
    _ensure_initialized()
    resolve_scope(user_role)
    return []


def list_mental_models(user_role: str) -> list[MentalModelView]:
    _ensure_initialized()
    scope = resolve_scope(user_role)
    models = []
    for item in read_mental_models(scope):
        get_value = item.get if isinstance(item, dict) else lambda key, default=None: getattr(item, key, default)
        model_id = str(get_value("id", ""))
        if not model_id:
            continue
        models.append(
            MentalModelView(
                model_id=model_id,
                name=str(get_value("name", model_id)),
                content=str(get_value("content", "") or ""),
                last_refreshed=get_value("last_refreshed_at"),
                evidence_count=0,
            )
        )
    return models


def get_memory_trace(query_id: str, user_role: str) -> MemoryTrace:
    _ensure_initialized()
    scope = resolve_scope(user_role)
    event = next(
        (row for row in list_audit_events(role=user_role) if row.get("query_id") == query_id),
        None,
    )
    if event is None:
        raise NotFoundError(f"Memory trace '{query_id}' was not found")
    if event.get("project_id"):
        assert_project_allowed(scope, event["project_id"])
    return MemoryTrace(
        query_id=query_id,
        recalled=[
            MemoryTraceRecalled(memory_id=str(memory_id))
            for memory_id in event.get("recalled_memory_ids", [])
        ],
    )


def ask_question(user_role: str, project_id: str, question: str) -> dict[str, Any]:
    """Recall relevant memories, build a simple decision brief, and record the audit event."""
    _ensure_initialized()
    scope = resolve_scope(user_role)
    assert_project_allowed(scope, project_id)

    bundle = recall_memories(question, scope, limit=5)
    source_ids = list(dict.fromkeys(item.source_id for item in bundle.results if item.source_id))
    recalled_memory_ids = [item.memory_id for item in bundle.results if item.memory_id]

    try:
        answer = reflect_on_question(question, scope, context=f"Project: {project_id}")
    except MemoryUnavailableError:
        answer = "No confident answer could be produced from the project memory."

    if not bundle.results:
        answer = "No confident answer could be produced from the project memory."

    query_id = f"query-{project_id}-{len(list_audit_events()) + 1}"
    record_audit_event(
        action="ask_question",
        role=user_role,
        project_id=project_id,
        query_id=query_id,
        decision_ids=[],
        output_hash=None,
        recalled_memory_ids=recalled_memory_ids,
        scope=scope,
        actor=user_role,
    )

    return {
        "query_id": query_id,
        "project_id": project_id,
        "question": question,
        "answer": answer.text if hasattr(answer, "text") else str(answer),
        "source_ids": source_ids,
        "decision_ids": source_ids,
        "retrieval_confidence": bundle.retrieval_confidence,
    }


def get_outcome_chain(user_role: str, decision_id: str):
    """Return a lightweight causal chain for a decision and its linked outcomes."""
    _ensure_initialized()
    scope = resolve_scope(user_role)
    decision = get_decision(decision_id, user_role)
    steps = [
        ChainStep(
            step_id=f"{decision_id}:decision",
            title=decision.title,
            date=decision.date,
            source_ids=decision.source_ids,
        )
    ]
    links = []
    for outcome in list_outcome_records(decision_id=decision_id):
        steps.append(
            ChainStep(
                step_id=str(outcome["outcome_id"]),
                title=outcome.get("title") or "Outcome",
                date=_as_datetime(outcome.get("created_at")),
                source_ids=[],
            )
        )
    for link in list_causal_link_records(decision_id=decision_id):
        label = str(link.get("relation") or "none").lower()
        if label not in {item.value for item in CausalLabel}:
            label = "none"
        links.append(
            CausalLink(
                decision_id=decision_id,
                outcome_id=link.get("outcome_id"),
                label=CausalLabel(label),
                rationale=link.get("relation") or "",
                evidence_ids=link.get("evidence_ids", []),
            )
        )
    assert_project_allowed(scope, decision.project_id)
    chain = OutcomeChain(chain_id=f"chain-{decision_id}", decision_id=decision_id, steps=steps, links=links)
    return {
        **chain.model_dump(mode="json"),
        "outcomes": [step.model_dump(mode="json") for step in steps[1:]],
    }


def list_drift_cards(user_role: str, project_id: str):
    """Compare persisted decisions with the current project constraints."""
    _ensure_initialized()
    scope = resolve_scope(user_role)
    assert_project_allowed(scope, project_id)
    try:
        current = get_project_context(project_id, user_role)
    except NotFoundError:
        return []
    if isinstance(current.constraints, dict):
        current = CurrentProjectContext(
            project_id=current.project_id,
            project_name=current.project_name,
            summary=current.summary,
            constraints=[Constraint(key=key, value=value) for key, value in current.constraints.items()],
            updated_at=current.updated_at,
        )
    results = []
    for decision in search_decisions(DecisionFilter(project_id=project_id), user_role):
        if not decision.constraints:
            continue
        result = score_drift(compare_constraints(decision, current))
        if result.level.value != "none":
            results.append(result)
    return results


def list_review_queue(user_role: str):
    """Return persisted review items; extraction review state is not stored yet."""
    _ensure_initialized()
    resolve_scope(user_role)
    return []


__all__ = [
    "get_memory_overview",
    "list_projects",
    "get_project_context",
    "search_decisions",
    "get_decision",
    "get_decision_timeline",
    "get_evidence",
    "list_observations",
    "list_mental_models",
    "get_memory_trace",
    "ingest_source",
    "ask_question",
    "update_project_context",
    "resolve_scope",
    "get_outcome_chain",
    "list_drift_cards",
    "list_review_queue",
    "ScopeError",
]
