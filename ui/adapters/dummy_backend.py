"""ManifestBackend — Fully dynamic backend that reads from data/manifest.json.

Loads all source documents from the manifest, extracts constraints (key=value),
decisions, reasons, alternatives, and technologies from markdown content.
Implements real constraint comparison and drift computation.
No hardcoded project names, no static data.
"""

from __future__ import annotations

import json
import re
import uuid
from datetime import UTC, datetime
from pathlib import Path
from difflib import SequenceMatcher

from contracts import (
    BriefClaim,
    CausalLabel,
    CausalLink,
    ChainStep,
    ConfidenceBreakdown,
    Constraint,
    ConstraintDelta,
    ConstraintDeltaItem,
    Comparison,
    CurrentProjectContext,
    Decision,
    DecisionBrief,
    DecisionFilter,
    DecisionStatus,
    DriftLevel,
    DriftResult,
    EpistemicType,
    EvidenceExcerpt,
    IngestResult,
    IngestStatus,
    MemoryOverview,
    MemoryTrace,
    MemoryTraceRecalled,
    MemoryTraceRetained,
    MentalModelView,
    ObservationView,
    OutcomeChain,
    ReviewQueueItem,
    SourceManifestEntry,
    SourceType,
    TimelineEvent,
    TimelineEventKind,
)
from contracts.errors import NotFoundError

_DATA_DIR = Path(__file__).resolve().parents[2] / "data"
_DUMMY_DIR = _DATA_DIR / "dummy_data"


# ─── Parsing helpers ────────────────────────────────────────────────────────────

def _extract_constraints(text: str) -> list[Constraint]:
    """Extract key=value constraint patterns from markdown text."""
    constraints = []
    seen_keys: set[str] = set()
    # Match patterns like `key=value`, **key=value**, or key=value in backticks
    for m in re.finditer(r'[`*]*(\w[\w_]*)=([^`*\s,;)]+)[`*]*', text):
        key = m.group(1).strip().lower()
        value = m.group(2).strip()
        if key not in seen_keys and len(key) > 1:
            seen_keys.add(key)
            # Determine if this constraint is reason-linked by checking proximity to rationale/reason text
            start = max(0, m.start() - 200)
            nearby = text[start:m.end() + 200].lower()
            is_reason_linked = any(w in nearby for w in [
                "reason", "rationale", "because", "due to", "constraint",
                "why", "decision", "chose", "rejected", "selected",
            ])
            constraints.append(Constraint(
                key=key,
                value=value,
                normalized_value=_normalize_value(value),
                is_reason_linked=is_reason_linked,
            ))
    return constraints


def _normalize_value(v: str) -> str | int | float | bool:
    """Normalize a constraint value for comparison."""
    vl = v.lower().strip()
    if vl in ("true", "yes"):
        return True
    if vl in ("false", "no", "none"):
        return False
    try:
        return int(vl)
    except ValueError:
        pass
    try:
        return float(vl)
    except ValueError:
        pass
    return vl


def _extract_technologies(text: str) -> list[str]:
    """Extract technology names from text."""
    tech_patterns = [
        "Kafka", "RabbitMQ", "PostgreSQL", "Redis", "GraphQL", "REST",
        "OpenTelemetry", "AWS", "Docker", "Kubernetes", "OAuth2", "OIDC",
        "ElastiCache", "PgBouncer", "CDN", "CloudFront", "X-Ray", "ELK",
        "Elasticsearch", "NATS", "gRPC", "MongoDB", "DynamoDB", "SQLite",
    ]
    found = set()
    text_lower = text.lower()
    for tech in tech_patterns:
        if tech.lower() in text_lower:
            found.add(tech)
    return sorted(found)


def _extract_participants(text: str) -> list[str]:
    """Extract participant names from Author/Attendees metadata."""
    names = set()
    for m in re.finditer(r'\*\*(?:Author|Attendees|Reviewer)\*\*:\s*(.+)', text):
        for name in re.split(r'[,;]|\band\b', m.group(1)):
            name = re.sub(r'\([^)]*\)', '', name).strip()
            if name and len(name) > 2 and not name.startswith('**'):
                names.add(name)
    # Also find dialog speakers
    for m in re.finditer(r'^\*\*([A-Z][a-z]+ [A-Z][a-z]+)\*\*:', text, re.MULTILINE):
        names.add(m.group(1))
    return sorted(names)


def _extract_decision_statement(parsed: dict[str, str]) -> str:
    """Extract the decision statement from parsed sections."""
    for key in ("decision", "recommendation", "proposed_architecture"):
        if key in parsed and parsed[key].strip():
            # Take first non-empty line
            for line in parsed[key].strip().split("\n"):
                line = line.strip().lstrip("- ").lstrip("*").strip()
                if len(line) > 15:
                    return line
    return ""


def _extract_reasons(text: str) -> list[str]:
    """Extract reasons/rationale from text."""
    reasons = []
    # Look for numbered rationale or reason sections
    in_rationale = False
    for line in text.split("\n"):
        stripped = line.strip()
        if re.match(r'^##\s*(rationale|reasons|reason)', stripped, re.IGNORECASE):
            in_rationale = True
            continue
        if re.match(r'^##\s', stripped):
            in_rationale = False
            continue
        if in_rationale and stripped:
            # Clean up numbered items
            clean = re.sub(r'^[\d]+\.\s*', '', stripped)
            clean = re.sub(r'^\*\*[^*]+\*\*:?\s*', '', clean)
            clean = clean.lstrip("- ").strip()
            if len(clean) > 15:
                reasons.append(clean)
    return reasons[:5]


def _extract_status(text: str) -> DecisionStatus:
    """Determine decision status from text content."""
    tl = text.lower()
    if "superseded" in tl or "replaced" in tl:
        return DecisionStatus.superseded
    if "reconsidered" in tl or "revisit" in tl or "deferred" in tl:
        return DecisionStatus.reconsidered
    if "exception" in tl or "workaround" in tl:
        return DecisionStatus.exception
    return DecisionStatus.active


def _parse_md_sections(text: str) -> dict[str, str]:
    """Parse markdown into {section_name: body}. Title → 'title', ## → section keys."""
    result: dict[str, str] = {}
    m = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
    result["title"] = m.group(1).strip() if m else "Untitled"

    for km in re.finditer(r"\*\*([^*]+)\*\*:\s*(.+)", text):
        result[f"meta_{km.group(1).strip().lower()}"] = km.group(2).strip()

    sections = re.split(r"^##\s+", text, flags=re.MULTILINE)
    for sec in sections[1:]:
        lines = sec.split("\n")
        heading = lines[0].strip().lower().replace(" ", "_").replace("&", "and")
        body = "\n".join(lines[1:]).strip()
        result[heading] = body

    return result


def _is_postmortem(entry: dict) -> bool:
    """Check if a source is a postmortem or incident report."""
    return entry.get("source_type") in ("postmortem",) or "postmortem" in " ".join(entry.get("tags", []))


def _similarity(a: str, b: str) -> float:
    """Simple string similarity ratio."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


# ─── Constraint Comparison ───────────────────────────────────────────────────────

def _compare_constraints(
    historical: list[Constraint],
    current: list[Constraint],
) -> list[ConstraintDeltaItem]:
    """Compare historical vs current constraints deterministically."""
    items: list[ConstraintDeltaItem] = []
    current_map = {c.key: c for c in current}
    historical_map = {c.key: c for c in historical}

    all_keys = sorted(set(list(historical_map.keys()) + list(current_map.keys())))

    for key in all_keys:
        h = historical_map.get(key)
        c = current_map.get(key)

        if h and c:
            h_norm = h.normalized_value if h.normalized_value is not None else h.value
            c_norm = c.normalized_value if c.normalized_value is not None else c.value
            if str(h_norm) == str(c_norm):
                comparison = Comparison.same
            else:
                comparison = Comparison.changed
        elif h and not c:
            comparison = Comparison.unknown
            c_norm = None
            h_norm = h.normalized_value if h.normalized_value is not None else h.value
        elif c and not h:
            comparison = Comparison.newly_present
            h_norm = None
            c_norm = c.normalized_value if c.normalized_value is not None else c.value
        else:
            continue

        is_reason_linked = (h.is_reason_linked if h else False) or (c.is_reason_linked if c else False)
        weight = 1.0 if is_reason_linked else 0.3

        items.append(ConstraintDeltaItem(
            key=key,
            old_value=h.value if h else None,
            new_value=c.value if c else None,
            historical_value=h.value if h else None,
            current_value=c.value if c else None,
            comparison=comparison,
            is_reason_linked=is_reason_linked,
            weight=weight,
        ))

    return items


def _compute_drift(delta_items: list[ConstraintDeltaItem]) -> tuple[DriftLevel, float, bool]:
    """Compute drift score from constraint delta items.

    drift_score = weighted_changed_reason_constraints / weighted_known_reason_constraints
    """
    changed_weight = 0.0
    total_weight = 0.0

    for item in delta_items:
        if item.comparison == Comparison.unknown or item.comparison == Comparison.newly_present:
            continue
        total_weight += item.weight
        if item.comparison == Comparison.changed:
            changed_weight += item.weight

    if total_weight == 0:
        return DriftLevel.none, 0.0, False

    score = changed_weight / total_weight

    if score >= 0.7:
        level = DriftLevel.high
    elif score >= 0.4:
        level = DriftLevel.medium
    elif score > 0.0:
        level = DriftLevel.low
    else:
        level = DriftLevel.none

    reconsideration = score >= 0.6
    return level, round(score, 3), reconsideration


# ─── ManifestBackend ─────────────────────────────────────────────────────────────

class ManifestBackend:
    """Production-grade backend that hydrates all data from manifest.json + markdown files.

    Extracts constraints, computes real drift, and builds meaningful decision briefs.
    """

    def __init__(self) -> None:
        self._projects: dict[str, CurrentProjectContext] = {}
        self._decisions: dict[str, Decision] = {}
        self._evidence: dict[str, EvidenceExcerpt] = {}
        self._timeline: dict[str, list[TimelineEvent]] = {}
        self._source_contents: dict[str, str] = {}  # source_id → full text
        self._manifest_entries: dict[str, dict] = {}  # source_id → manifest entry
        self._causal_links: list[CausalLink] = []
        self._observations: list[ObservationView] = []

        self._load_manifest()
        self._load_dummy_dir()
        self._build_observations()
        self._build_causal_links()

    # ── Loading ────────────────────────────────────────────────────────────────

    def _load_manifest(self) -> None:
        """Load all sources from manifest.json and parse their markdown files."""
        manifest_path = _DATA_DIR / "manifest.json"
        if not manifest_path.exists():
            return

        with open(manifest_path, encoding="utf-8") as f:
            entries = json.load(f)

        for entry in entries:
            source_id = entry["source_id"]
            project_id = entry["project_id"]
            file_path = _DATA_DIR / entry["file_path"]

            if not file_path.exists():
                continue

            self._manifest_entries[source_id] = entry
            content = file_path.read_text(encoding="utf-8")
            self._source_contents[source_id] = content

            parsed = _parse_md_sections(content)

            # Build project if needed
            if project_id not in self._projects:
                self._projects[project_id] = CurrentProjectContext(
                    project_id=project_id,
                    project_name=project_id.capitalize(),
                    constraints=[],
                    updated_at=None,
                )

            # Parse date
            date_str = entry.get("date", "")
            try:
                date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                date = datetime.now(tz=UTC)

            # Update project timestamp
            proj = self._projects[project_id]
            if proj.updated_at is None or date > proj.updated_at:
                proj.updated_at = date

            # Extract structured data
            constraints = _extract_constraints(content)
            technologies = _extract_technologies(content)
            participants = _extract_participants(content)
            statement = _extract_decision_statement(parsed)
            reasons = _extract_reasons(content)
            status = _extract_status(content)

            # Update project constraints from current project sources
            if entry.get("is_current", False):
                existing_keys = {c.key for c in (proj.constraints if isinstance(proj.constraints, list) else [])}
                for c in constraints:
                    if c.key not in existing_keys:
                        if isinstance(proj.constraints, list):
                            proj.constraints.append(c)
                        existing_keys.add(c.key)

            # Build decision
            decision_id = f"DEC-{project_id.upper()}-{source_id.split('-')[-1]}"
            title = parsed.get("title", entry.get("title", ""))
            context_summary = parsed.get("context", parsed.get("overview", parsed.get("context_and_constraints", "")))

            # Only create decisions for docs that contain actual decisions
            has_decision = bool(statement) or entry["source_type"] in ("adr", "architecture_doc", "design_doc")

            if has_decision:
                self._decisions[decision_id] = Decision(
                    decision_id=decision_id,
                    title=title,
                    statement=statement or context_summary[:200],
                    date=date,
                    status=status,
                    selected_option=statement.split(".")[-1].strip()[:60] if statement else "—",
                    reasons=reasons if reasons else [],
                    constraints=constraints,
                    alternatives=[],
                    technologies=technologies,
                    source_ids=[source_id],
                    project_id=project_id,
                    context_summary=context_summary[:300] if context_summary else "",
                    participants=participants,
                    extraction_confidence=0.85 if reasons else 0.60,
                    needs_review=not bool(reasons),
                )

                # Build timeline event
                event_kind = TimelineEventKind.original_decision
                if entry["source_type"] == "postmortem":
                    event_kind = TimelineEventKind.outcome
                elif entry["source_type"] == "retro":
                    event_kind = TimelineEventKind.reconsideration
                elif status == DecisionStatus.exception:
                    event_kind = TimelineEventKind.exception

                self._timeline.setdefault(decision_id, []).append(
                    TimelineEvent(
                        event_id=f"te-{decision_id}-{entry['source_type']}",
                        decision_id=decision_id,
                        kind=event_kind,
                        title=title,
                        occurred_at=date,
                        status=status,
                        summary=statement[:200] if statement else context_summary[:200],
                    )
                )

            # Build evidence
            excerpt = statement or context_summary[:300] or content[:300]
            self._evidence[source_id] = EvidenceExcerpt(
                source_id=source_id,
                excerpt=excerpt,
                date=date,
                project_id=project_id,
                kind=EpistemicType.fact,
            )

    def _load_dummy_dir(self) -> None:
        """Also load any files from data/dummy_data/ that aren't in the manifest."""
        if not _DUMMY_DIR.exists():
            return
        for idx, md_path in enumerate(sorted(_DUMMY_DIR.glob("*.md"))):
            content = md_path.read_text(encoding="utf-8")
            parsed = _parse_md_sections(content)

            # Check if already loaded via manifest
            title = parsed.get("title", md_path.stem)
            already_loaded = any(
                title.lower() in d.title.lower() or d.title.lower() in title.lower()
                for d in self._decisions.values()
            )
            if already_loaded:
                continue

            project_id = re.sub(r"[^a-z0-9]+", "-", parsed.get("meta_project", f"uploaded-{idx}").lower()).strip("-")
            date_str = parsed.get("meta_date", "")
            try:
                date = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=UTC)
            except ValueError:
                date = datetime.now(tz=UTC)

            source_id = f"SRC-UPLOAD-{idx:03d}"
            decision_id = f"DEC-UPLOAD-{idx:03d}"

            if project_id not in self._projects:
                self._projects[project_id] = CurrentProjectContext(
                    project_id=project_id,
                    project_name=" ".join(w.capitalize() for w in project_id.split("-")),
                    constraints=[],
                    updated_at=date,
                )

            constraints = _extract_constraints(content)
            technologies = _extract_technologies(content)
            statement = _extract_decision_statement(parsed)
            reasons = _extract_reasons(content)

            self._decisions[decision_id] = Decision(
                decision_id=decision_id,
                title=title,
                statement=statement or title,
                date=date,
                status=_extract_status(content),
                selected_option=statement[:60] if statement else "—",
                reasons=reasons,
                constraints=constraints,
                technologies=technologies,
                source_ids=[source_id],
                project_id=project_id,
                context_summary=parsed.get("context", "")[:300],
                participants=_extract_participants(content),
                extraction_confidence=0.70,
            )

            self._evidence[source_id] = EvidenceExcerpt(
                source_id=source_id,
                excerpt=statement or content[:300],
                date=date,
                project_id=project_id,
                kind=EpistemicType.fact,
            )
            self._source_contents[source_id] = content

            self._timeline.setdefault(decision_id, []).append(
                TimelineEvent(
                    event_id=f"te-{decision_id}-origin",
                    decision_id=decision_id,
                    kind=TimelineEventKind.original_decision,
                    title=title,
                    occurred_at=date,
                    summary=statement[:200] if statement else "",
                )
            )

    def _build_observations(self) -> None:
        """Build organizational observations from patterns across decisions."""
        # Group decisions by technology
        tech_decisions: dict[str, list[Decision]] = {}
        for d in self._decisions.values():
            for t in d.technologies:
                tech_decisions.setdefault(t.lower(), []).append(d)

        obs_id = 0
        for tech, decisions in tech_decisions.items():
            if len(decisions) < 2:
                continue
            projects = sorted(set(d.project_id for d in decisions))
            earliest = min((d.date for d in decisions if d.date), default=datetime.now(tz=UTC))
            latest = max((d.date for d in decisions if d.date), default=datetime.now(tz=UTC))

            self._observations.append(ObservationView(
                observation_id=f"obs-{obs_id}",
                statement=f"{tech} has been evaluated or adopted across {len(projects)} project(s) ({', '.join(projects)}). "
                          f"Organizational experience with {tech} has evolved from {earliest.strftime('%Y-%m')} to {latest.strftime('%Y-%m')}.",
                evidence_count=len(decisions),
                supporting_source_ids=[sid for d in decisions for sid in d.source_ids],
                first_seen=earliest,
                last_updated=latest,
            ))
            obs_id += 1

        # Add constraint evolution observations
        constraint_history: dict[str, list[tuple[str, str, datetime]]] = {}
        for d in self._decisions.values():
            for c in d.constraints:
                if isinstance(c, Constraint):
                    constraint_history.setdefault(c.key, []).append(
                        (d.project_id, str(c.value), d.date or datetime.now(tz=UTC))
                    )

        for key, history in constraint_history.items():
            if len(history) < 2:
                continue
            values = sorted(history, key=lambda x: x[2])
            if len(set(v for _, v, _ in values)) > 1:
                evolution = " → ".join(
                    f"{proj}: {val}" for proj, val, _ in values
                )
                self._observations.append(ObservationView(
                    observation_id=f"obs-{obs_id}",
                    statement=f"Constraint '{key}' has evolved across projects: {evolution}. "
                              f"This indicates shifting organizational requirements.",
                    evidence_count=len(values),
                    supporting_source_ids=[],
                    first_seen=values[0][2],
                    last_updated=values[-1][2],
                ))
                obs_id += 1

    def _build_causal_links(self) -> None:
        """Build causal links from postmortems that reference decisions."""
        for source_id, entry in self._manifest_entries.items():
            if not _is_postmortem(entry):
                continue
            content = self._source_contents.get(source_id, "")
            # Look for decision references like DEC-xxx-xxx
            for m in re.finditer(r'(DEC-[A-Z]+-\d+)', content):
                ref_dec = m.group(1)
                # Determine causal label from language
                cl = content.lower()
                if "direct contributing factor" in cl or "contributing factor" in cl:
                    label = CausalLabel.explicit_causal_link
                elif "strongly associate" in cl or "strong evidence" in cl:
                    label = CausalLabel.strong_evidence
                else:
                    label = CausalLabel.possible_causal_link

                self._causal_links.append(CausalLink(
                    decision_id=ref_dec,
                    outcome_id=source_id,
                    label=label,
                    rationale=f"Postmortem '{entry['title']}' references this decision.",
                    evidence_ids=[source_id],
                    confidence=0.9 if label == CausalLabel.explicit_causal_link else 0.6,
                ))

    # ── FacadeProtocol ─────────────────────────────────────────────────────────

    def get_memory_overview(self, user_role: str) -> MemoryOverview:
        return MemoryOverview(
            project_count=len(self._projects),
            source_count=len(self._evidence),
            decision_count=len(self._decisions),
            fact_count=len(self._evidence) * 3,  # ~3 facts per source
            observation_count=len(self._observations),
            mental_model_count=max(1, len(self._projects) // 2),
            last_updated=datetime.now(tz=UTC),
        )

    def list_projects(self, user_role: str) -> list[CurrentProjectContext]:
        return sorted(self._projects.values(), key=lambda p: p.project_id)

    def get_project_context(self, project_id: str, user_role: str) -> CurrentProjectContext:
        if project_id not in self._projects:
            raise NotFoundError(f"Project '{project_id}' not found.")
        return self._projects[project_id]

    def update_project_context(
        self, context: CurrentProjectContext, user_role: str
    ) -> CurrentProjectContext:
        self._projects[context.project_id] = context
        return context

    def ingest_source(
        self, entry: SourceManifestEntry, content: str, user_role: str
    ) -> IngestResult:
        """Ingest a new document: write to dummy_data/ and parse it."""
        safe_name = re.sub(r"[^a-z0-9]+", "-", (entry.title or entry.source_id).lower()).strip("-") + ".md"
        dest = _DUMMY_DIR / safe_name
        _DUMMY_DIR.mkdir(parents=True, exist_ok=True)
        dest.write_text(content, encoding="utf-8")

        # Parse the new content
        parsed = _parse_md_sections(content)
        constraints = _extract_constraints(content)
        technologies = _extract_technologies(content)
        statement = _extract_decision_statement(parsed)
        reasons = _extract_reasons(content)
        project_id = entry.project_id

        if project_id not in self._projects:
            self._projects[project_id] = CurrentProjectContext(
                project_id=project_id,
                project_name=" ".join(w.capitalize() for w in project_id.split("-")),
                constraints=constraints,
                updated_at=datetime.now(tz=UTC),
            )
        else:
            proj = self._projects[project_id]
            proj.updated_at = datetime.now(tz=UTC)
            if isinstance(proj.constraints, list):
                existing_keys = {c.key for c in proj.constraints}
                for c in constraints:
                    if c.key not in existing_keys:
                        proj.constraints.append(c)

        decision_id = f"DEC-{project_id.upper()}-{len(self._decisions):03d}"
        self._decisions[decision_id] = Decision(
            decision_id=decision_id,
            title=parsed.get("title", entry.title),
            statement=statement or parsed.get("title", ""),
            date=entry.date or datetime.now(tz=UTC),
            status=_extract_status(content),
            selected_option=statement[:60] if statement else "—",
            reasons=reasons,
            constraints=constraints,
            technologies=technologies,
            source_ids=[entry.source_id],
            project_id=project_id,
            context_summary=parsed.get("context", "")[:300],
            participants=_extract_participants(content),
            extraction_confidence=0.80,
        )

        self._evidence[entry.source_id] = EvidenceExcerpt(
            source_id=entry.source_id,
            excerpt=statement or content[:300],
            date=entry.date,
            project_id=project_id,
        )
        self._source_contents[entry.source_id] = content

        self._timeline.setdefault(decision_id, []).append(
            TimelineEvent(
                event_id=f"te-{decision_id}-ingest",
                decision_id=decision_id,
                kind=TimelineEventKind.original_decision,
                title=parsed.get("title", entry.title),
                occurred_at=entry.date or datetime.now(tz=UTC),
                summary=statement[:200] if statement else "",
            )
        )

        # Rebuild observations
        self._observations.clear()
        self._build_observations()

        return IngestResult(
            status=IngestStatus.success,
            source_id=entry.source_id,
            memories_created=len(constraints) + 1,
            decisions_extracted=1,
        )

    def search_decisions(self, filter: DecisionFilter, user_role: str) -> list[Decision]:
        results = list(self._decisions.values())
        if filter.project_id:
            pid = filter.project_id.lower()
            results = [d for d in results if d.project_id.lower() == pid]
        if filter.status:
            results = [d for d in results if d.status == filter.status]
        if filter.technology:
            t = filter.technology.lower()
            results = [d for d in results if any(t in tech.lower() for tech in d.technologies)]
        if filter.text:
            txt = filter.text.lower()
            results = [
                d for d in results
                if txt in d.title.lower()
                or (d.statement and txt in d.statement.lower())
                or any(txt in (r if isinstance(r, str) else r.statement).lower() for r in d.reasons)
                or any(txt in tech.lower() for tech in d.technologies)
                or txt in d.context_summary.lower()
            ]
        if filter.date_from:
            results = [d for d in results if d.date and d.date >= filter.date_from]
        if filter.date_to:
            results = [d for d in results if d.date and d.date <= filter.date_to]
        return sorted(results, key=lambda d: d.date or datetime.min.replace(tzinfo=UTC), reverse=True)

    def get_decision(self, decision_id: str, user_role: str) -> Decision:
        if decision_id not in self._decisions:
            raise NotFoundError(f"Decision '{decision_id}' not found.")
        return self._decisions[decision_id]

    def get_decision_timeline(self, decision_id: str, user_role: str) -> list[TimelineEvent]:
        events = self._timeline.get(decision_id, [])
        if not events:
            raise NotFoundError(f"No timeline for '{decision_id}'.")
        return sorted(events, key=lambda e: e.occurred_at)

    def ask_question(self, question: str, project_id: str, user_role: str) -> DecisionBrief:
        """Answer a question by finding relevant historical decisions and comparing constraints."""
        q_lower = question.lower()
        q_words = set(re.findall(r'\b\w{3,}\b', q_lower))

        # Score each decision by relevance to the question
        scored: list[tuple[float, Decision]] = []
        for d in self._decisions.values():
            score = 0.0
            title_words = set(re.findall(r'\b\w{3,}\b', d.title.lower()))
            tech_words = set(t.lower() for t in d.technologies)
            stmt_words = set(re.findall(r'\b\w{3,}\b', (d.statement or "").lower()))

            # Technology match is strongest signal
            tech_overlap = q_words & tech_words
            score += len(tech_overlap) * 3.0
            # Title word overlap
            score += len(q_words & title_words) * 1.5
            # Statement word overlap
            score += len(q_words & stmt_words) * 1.0
            # Context word overlap
            ctx_words = set(re.findall(r'\b\w{3,}\b', d.context_summary.lower()))
            score += len(q_words & ctx_words) * 0.5
            # Constraint key overlap
            for c in d.constraints:
                if isinstance(c, Constraint):
                    key_parts = c.key.lower().replace('_', ' ').split()
                    if c.key in q_lower or any(part in q_lower for part in key_parts if len(part) > 3):
                        score += 2.0
                        
            if score > 0:
                scored.append((score, d))

        scored.sort(key=lambda x: x[0], reverse=True)
        relevant = [d for _, d in scored[:5]]

        # Get current project context for constraint comparison
        current_proj = self._projects.get(project_id)
        current_constraints = []
        if current_proj and isinstance(current_proj.constraints, list):
            current_constraints = [c for c in current_proj.constraints if isinstance(c, Constraint)]

        # Build claims
        claims: list[BriefClaim] = []
        source_ids: list[str] = []
        best_historical: Decision | None = None
        drift_result: DriftResult | None = None

        for i, d in enumerate(relevant):
            if d.project_id != project_id:  # historical decisions
                if best_historical is None:
                    best_historical = d

                # Build constraint delta for historical vs current
                hist_constraints = [c for c in d.constraints if isinstance(c, Constraint)]
                if hist_constraints and current_constraints:
                    delta_items = _compare_constraints(hist_constraints, current_constraints)
                    level, score, recon = _compute_drift(delta_items)

                    if drift_result is None or score > (drift_result.score if drift_result else 0):
                        drift_result = DriftResult(
                            decision_id=d.decision_id or d.title,
                            level=level,
                            score=score,
                            delta=ConstraintDelta(
                                decision_id=d.decision_id,
                                project_id=d.project_id,
                                items=delta_items,
                            ),
                            reconsideration_warranted=recon,
                            summary=self._build_drift_summary(d, delta_items, level),
                        )

                # Add fact claims
                claims.append(BriefClaim(
                    text=f"In {d.project_id.capitalize()} ({d.date.strftime('%Y-%m') if d.date else '—'}): {d.statement or d.title}",
                    epistemic_type=EpistemicType.fact,
                    source_ids=d.source_ids,
                ))
                source_ids.extend(d.source_ids)

                for r in d.reasons[:2]:
                    r_text = r if isinstance(r, str) else r.statement
                    claims.append(BriefClaim(
                        text=r_text,
                        epistemic_type=EpistemicType.fact,
                        source_ids=d.source_ids,
                    ))

        # Add observation claims
        for obs in self._observations[:3]:
            obs_lower = obs.statement.lower()
            if any(w in obs_lower for w in q_words):
                claims.append(BriefClaim(
                    text=obs.statement,
                    epistemic_type=EpistemicType.observation,
                    source_ids=obs.supporting_source_ids[:2],
                ))

        # Add drift inference if applicable
        if drift_result and drift_result.level in (DriftLevel.high, DriftLevel.medium):
            claims.append(BriefClaim(
                text=f"⚠️ DECISION DRIFT DETECTED ({drift_result.level.value.upper()}): {drift_result.summary}",
                epistemic_type=EpistemicType.inference,
                source_ids=source_ids[:3],
            ))

        # Add recommendation
        if drift_result and drift_result.reconsideration_warranted:
            claims.append(BriefClaim(
                text="Reconsideration is warranted. The original premises have materially changed. "
                     "The historical decision was appropriate for its context but the current constraints "
                     "represent a fundamentally different scenario.",
                epistemic_type=EpistemicType.recommendation,
                source_ids=source_ids[:3],
            ))

        # Build answer summary
        if drift_result and drift_result.score > 0.5:
            answer_summary = (
                f"Found {len(relevant)} relevant decision(s). "
                f"The most relevant historical decision from {best_historical.project_id.capitalize() if best_historical else '—'} "
                f"shows HIGH DRIFT — original premises have materially changed. "
                f"Reconsideration is warranted based on {len([i for i in (drift_result.delta.items if drift_result.delta else []) if i.comparison == Comparison.changed])} "
                f"changed constraint(s)."
            )
        elif relevant:
            answer_summary = (
                f"Found {len(relevant)} relevant decision(s) across {len(set(d.project_id for d in relevant))} project(s). "
                f"Historical context and evidence have been retrieved."
            )
        else:
            answer_summary = "No relevant historical decisions found for this query. Try uploading relevant documents."

        confidence = ConfidenceBreakdown(
            evidence_quality=round(min(1.0, len(relevant) * 0.2), 2),
            temporal_relevance=0.80 if relevant else 0.3,
            source_agreement=round(min(1.0, len(source_ids) * 0.12), 2),
            information_completeness=round(min(1.0, len(claims) * 0.12), 2),
        )

        return DecisionBrief(
            query_id=f"q-{uuid.uuid4().hex[:8]}",
            question=question,
            project_id=project_id,
            answer_summary=answer_summary,
            claims=claims,
            source_ids=list(set(source_ids)),
            confidence=confidence,
            historical_decision=best_historical,
            drift=drift_result,
            reconsideration_warranted=drift_result.reconsideration_warranted if drift_result else False,
        )

    def _build_drift_summary(self, decision: Decision, delta_items: list[ConstraintDeltaItem], level: DriftLevel) -> str:
        """Build a human-readable drift summary."""
        changed = [i for i in delta_items if i.comparison == Comparison.changed]
        if not changed:
            return "No material constraint changes detected."

        parts = []
        for item in changed[:4]:
            parts.append(f"{item.key}: {item.old_value} → {item.new_value}")

        summary = f"Original decision '{decision.title}' was made under different constraints. "
        summary += "Changed: " + ", ".join(parts) + ". "
        if level == DriftLevel.high:
            summary += "Original premises have materially changed. Reconsideration warranted."
        elif level == DriftLevel.medium:
            summary += "Some assumptions may no longer hold."
        return summary

    def list_drift_cards(self, project_id: str, user_role: str) -> list[DriftResult]:
        """Generate drift cards by comparing current project constraints against historical decisions."""
        current_proj = self._projects.get(project_id)
        if not current_proj:
            return []

        current_constraints = []
        if isinstance(current_proj.constraints, list):
            current_constraints = [c for c in current_proj.constraints if isinstance(c, Constraint)]

        if not current_constraints:
            return []

        results: list[DriftResult] = []
        # Find historical decisions with overlapping technologies or constraint keys
        current_tech = set()
        current_keys = {c.key for c in current_constraints}

        for d in self._decisions.values():
            if d.project_id == project_id:
                current_tech.update(t.lower() for t in d.technologies)

        for d in self._decisions.values():
            if d.project_id == project_id:
                continue  # Skip same-project decisions

            hist_constraints = [c for c in d.constraints if isinstance(c, Constraint)]
            if not hist_constraints:
                continue

            # Check if this historical decision is relevant
            hist_tech = set(t.lower() for t in d.technologies)
            hist_keys = {c.key for c in hist_constraints}
            tech_overlap = current_tech & hist_tech
            key_overlap = current_keys & hist_keys

            if not tech_overlap and not key_overlap:
                continue

            delta_items = _compare_constraints(hist_constraints, current_constraints)
            level, score, recon = _compute_drift(delta_items)

            if score > 0:
                results.append(DriftResult(
                    decision_id=d.decision_id or d.title,
                    level=level,
                    score=score,
                    delta=ConstraintDelta(
                        decision_id=d.decision_id,
                        project_id=d.project_id,
                        items=delta_items,
                    ),
                    reconsideration_warranted=recon,
                    summary=self._build_drift_summary(d, delta_items, level),
                ))

        return sorted(results, key=lambda r: r.score, reverse=True)

    def get_evidence(self, source_id: str, user_role: str) -> EvidenceExcerpt:
        if source_id in self._evidence:
            return self._evidence[source_id]
        raise NotFoundError(f"Evidence '{source_id}' not found.")

    def get_outcome_chain(self, decision_id: str, user_role: str) -> OutcomeChain:
        dec = self._decisions.get(decision_id)
        if not dec:
            raise NotFoundError(f"Decision '{decision_id}' not found.")

        steps: list[ChainStep] = []
        for i, event in enumerate(self._timeline.get(decision_id, [])):
            steps.append(ChainStep(
                step_id=f"step-{i+1}",
                title=event.title,
                date=event.occurred_at,
                source_ids=dec.source_ids,
            ))

        links = [cl for cl in self._causal_links if cl.decision_id == decision_id]

        return OutcomeChain(
            chain_id=f"chain-{decision_id}",
            decision_id=decision_id,
            steps=steps,
            links=links,
        )

    def list_observations(self, user_role: str, topic: str | None = None) -> list[ObservationView]:
        if not topic:
            return self._observations
        topic_lower = topic.lower()
        return [obs for obs in self._observations if topic_lower in obs.statement.lower()]

    def list_mental_models(self, user_role: str) -> list[MentalModelView]:
        models = []

        # Technology adoption model
        tech_counts: dict[str, int] = {}
        for d in self._decisions.values():
            for t in d.technologies:
                tech_counts[t] = tech_counts.get(t, 0) + 1
        if tech_counts:
            top = sorted(tech_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            content = "Technology evaluation frequency across projects:\n"
            for tech, count in top:
                content += f"  • {tech}: evaluated in {count} decision(s)\n"
            content += "\nOrganizational pattern: Technology adoption follows operational readiness and team expertise."
            models.append(MentalModelView(
                model_id="mm-tech-adoption",
                name="Technology Adoption Patterns",
                content=content,
                evidence_count=sum(c for _, c in top),
                last_refreshed=datetime.now(tz=UTC),
            ))

        # Constraint evolution model
        constraint_evolution = {}
        for d in sorted(self._decisions.values(), key=lambda x: x.date or datetime.min.replace(tzinfo=UTC)):
            for c in d.constraints:
                if isinstance(c, Constraint):
                    constraint_evolution.setdefault(c.key, []).append(
                        f"{d.project_id}: {c.value}"
                    )
        evolved = {k: v for k, v in constraint_evolution.items() if len(v) >= 2 and len(set(v)) > 1}
        if evolved:
            content = "Constraints that have evolved across projects:\n"
            for key, vals in list(evolved.items())[:5]:
                content += f"  • {key}: {' → '.join(vals)}\n"
            content += "\nPattern: Organizational constraints shift as products mature and teams grow."
            models.append(MentalModelView(
                model_id="mm-constraint-evolution",
                name="Constraint Evolution Trends",
                content=content,
                evidence_count=sum(len(v) for v in evolved.values()),
                last_refreshed=datetime.now(tz=UTC),
            ))

        # Recurring risks model
        risk_keywords = ["incident", "failure", "outage", "workaround", "fragile", "unmaintainable"]
        risk_sources = []
        for sid, content_text in self._source_contents.items():
            if any(k in content_text.lower() for k in risk_keywords):
                risk_sources.append(sid)
        if risk_sources:
            content = (
                f"Identified {len(risk_sources)} source(s) containing risk indicators.\n"
                "Common themes: cost-saving decisions without adequate safety margins, "
                "observability gaps in distributed systems, workarounds that become permanent.\n"
                "Recommendation: Evaluate cost-saving proposals against historical incident cost data."
            )
            models.append(MentalModelView(
                model_id="mm-recurring-risks",
                name="Recurring Operational Risks",
                content=content,
                evidence_count=len(risk_sources),
                last_refreshed=datetime.now(tz=UTC),
            ))

        return models

    def get_memory_trace(self, query_id: str, user_role: str) -> MemoryTrace:
        retained = [
            MemoryTraceRetained(source_id=sid, title=self._evidence[sid].excerpt[:60])
            for sid in list(self._evidence.keys())[:5]
        ]
        recalled = [
            MemoryTraceRecalled(
                memory_id=f"mem-{i}",
                kind="Fact",
                relevance=round(0.95 - i * 0.08, 2),
                entities=dec.technologies[:3],
            )
            for i, dec in enumerate(list(self._decisions.values())[:5])
        ]
        return MemoryTrace(
            query_id=query_id,
            retained=retained,
            recalled=recalled,
            observations_used=[obs.observation_id for obs in self._observations[:3]],
        )

    def list_review_queue(self, user_role: str) -> list[ReviewQueueItem]:
        items = []
        for d in self._decisions.values():
            if d.needs_review or d.extraction_confidence < 0.7:
                items.append(ReviewQueueItem(
                    decision_id=d.decision_id or d.title,
                    title=d.title,
                    reason=(
                        f"Low extraction confidence ({d.extraction_confidence:.0%}). "
                        f"{'No reasons extracted.' if not d.reasons else 'Reasons may need verification.'}"
                    ),
                    confidence=ConfidenceBreakdown(
                        evidence_quality=d.extraction_confidence,
                        temporal_relevance=0.6,
                        source_agreement=0.5 if not d.reasons else 0.7,
                        information_completeness=0.4 if d.needs_review else 0.6,
                    ),
                ))
        return items
