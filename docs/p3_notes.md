# DecisionPrint P3 Corpus Bible

This is the CORPUS BIBLE — the single source of truth for the entire fictional world. It must be thorough, internally consistent, and ready to drive document creation in Stage 1.

## Company
- **Northstar Systems** — B2B enterprise platform company
- Founded 2019, ~200 engineers, 4 platform teams
- Sells a multi-tenant SaaS platform for logistics and supply chain management
- HQ: Austin, TX

## Timeline
2024-01 to 2026-09 (present)

## People (8-10 synthetic names, consistent everywhere)
| Name | Role | Team | Notes |
|---|---|---|---|
| Marcus Chen | CTO | Leadership | Final technical authority |
| Sarah Okonkwo | VP Engineering | Leadership | Budget owner |
| Raj Patel | Staff Engineer | Platform | Kafka/messaging expert, drove Alpha |
| Elena Vasquez | Engineering Manager | Platform | Nova project lead |
| David Kim | Senior SRE | Infrastructure | Ops capacity concerns |
| Priya Sharma | Staff Engineer | Data | Redis/caching architect |
| James Morrison | Tech Lead | API | GraphQL evaluation lead |
| Aisha Rahman | Senior Engineer | Platform | Cedar cost optimization |
| Tom Bradley | Director of Engineering | All | Process governance |
| Lisa Nguyen | Product Manager | Product | Business requirements |

## Projects
| Slug | Name | Status | Start | End | Description |
|---|---|---|---|---|---|
| `alpha` | Project Alpha | historical | 2024-03-01 | 2024-09-30 | Platform v2 — messaging architecture redesign |
| `beta` | Project Beta | historical | 2024-06-15 | 2025-01-31 | API gateway modernization |
| `gamma` | Project Gamma | historical | 2025-01-15 | 2025-06-30 | Caching layer overhaul |
| `delta` | Project Delta | historical | 2025-03-01 | 2025-09-30 | Infrastructure cost optimization |
| `nova` | Project Nova | current | 2026-01-15 | present | Next-gen event platform |

## Five Decision Chains

### Chain 1: Kafka (Alpha → Beta → Nova) — THE DEMO CHAIN
**Arc:** Kafka rejected in Alpha when scale was small → async needs grew through Beta → Nova's scale makes Kafka the obvious choice now. Drift: HIGH.

| Constraint Key | Alpha (2024) | Beta (2024) | Nova (2026) |
|---|---|---|---|
| `consumer_count` | 2 | 5 | 15 |
| `replay_required` | false | false | true |
| `traffic_volume` | moderate | moderate-high | high |
| `ops_capacity` | small (3 SREs) | small (4 SREs) | medium (8 SREs) |
| `async_workflows` | false | limited | true |

- **Alpha decision (DEC-ALPHA-001):** Reject Kafka, use simple RabbitMQ. Reasons: complexity overhead for 2 consumers, team unfamiliar, ops too small.
- **Beta exception:** Added async job queue workaround (not Kafka) for growing event needs.
- **Nova context:** 15 consumers, replay needed for audit trail, high traffic, team now has Kafka experience. ALL original rejection reasons invalidated.
- **Expected drift:** HIGH, reconsideration_warranted=True

### Chain 2: Cedar / Backup Policy (Delta) — THE CAUSAL CHAIN
**Arc:** Cost-cutting removed backups → database failure → postmortem explicitly names missing backups as contributing factor. Causal label: EXPLICIT_CAUSAL_LINK.

| Constraint Key | Delta (2025) | After Incident |
|---|---|---|
| `backup_policy` | none (removed for cost) | daily_incremental |
| `budget_pressure` | high | reduced (lesson learned) |
| `data_criticality` | medium (underestimated) | high |

- **Delta decision (DEC-DELTA-001):** Remove automated backups to save $4,200/month. Aisha Rahman proposed.
- **Implementation:** Backups disabled 2025-04-15.
- **Incident:** 2025-07-22 database corruption, 6-hour outage, partial data loss.
- **Postmortem:** EXPLICITLY states "The removal of automated backups (DEC-DELTA-001) was a direct contributing factor to the extended recovery time and partial data loss."
- **Consequence:** Backups restored with enhanced policy, budget allocated.

### Chain 3: Redis (Alpha → Gamma → Nova)
**Arc:** Single Redis → 4 instances → 20 instances; scaling pattern.

| Constraint Key | Alpha (2024) | Gamma (2025) | Nova (2026) |
|---|---|---|---|
| `instance_count` | 1 | 4 | 20 |
| `cache_hit_ratio` | 0.85 | 0.72 (degrading) | target 0.90 |
| `session_persistence` | false | true | true |

- **Alpha decision (DEC-ALPHA-002):** Single Redis instance sufficient.
- **Gamma decision (DEC-GAMMA-001):** Scale to Redis Cluster (4 instances). Cache hit ratio was degrading.
- **Nova context:** 20 instances planned, need session persistence + high availability.
- **Expected drift:** MEDIUM (scaling, not architectural shift)

### Chain 4: GraphQL (Beta → Nova)
**Arc:** GraphQL rejected for known clients → partner ecosystem changes client diversity, but decision STAYS REJECTED for schema complexity reasons. Proves "drift ≠ forced reversal."

| Constraint Key | Beta (2024) | Nova (2026) |
|---|---|---|
| `client_count` | 3 (known) | 12 (including partners) |
| `client_diversity` | internal_only | partner_ecosystem |
| `schema_complexity` | low | high (still a problem) |

- **Beta decision (DEC-BETA-001):** Reject GraphQL, use REST. Reasons: (1) only 3 known clients, (2) schema complexity unwarranted, (3) team lacks GraphQL expertise.
- **Nova context:** client_count drifted significantly BUT schema_complexity is now even higher. Decision stays rejected for reason (2) — a NON-constraint reason still applies.
- **Expected drift:** MEDIUM (some constraints changed, but rejection still valid)
- **reconsideration_warranted:** False (key rejection reason unchanged)

### Chain 5: Tracing (Alpha → Beta → Nova)
**Arc:** logs_only → partial tracing → full observability; debugging delays drove the change.

| Constraint Key | Alpha (2024) | Beta (2024-25) | Nova (2026) |
|---|---|---|---|
| `observability_maturity` | logs_only | partial_tracing | full_tracing |
| `debugging_frequency` | weekly | daily | continuous |
| `incident_mttr` | 4h | 2h | target <30m |

- **Alpha decision (DEC-ALPHA-003):** Structured logging sufficient, no distributed tracing. Reasons: small service count, low debugging frequency.
- **Beta exception:** Added partial tracing for API gateway after repeated debugging delays.
- **Nova context:** 40+ microservices, continuous monitoring needed.
- **Expected drift:** HIGH, reconsideration_warranted=True

## Decision IDs Planned
| ID | Chain | Project | Title |
|---|---|---|---|
| DEC-ALPHA-001 | Kafka | alpha | Reject Kafka for messaging |
| DEC-ALPHA-002 | Redis | alpha | Single Redis instance |
| DEC-ALPHA-003 | Tracing | alpha | Structured logging over tracing |
| DEC-BETA-001 | GraphQL | beta | Reject GraphQL for API layer |
| DEC-GAMMA-001 | Redis | gamma | Scale to Redis Cluster |
| DEC-DELTA-001 | Cedar | delta | Remove automated backups |

## Source IDs Planned (Tier 1 — Kafka + Cedar)
| Source ID | Project | Type | Title |
|---|---|---|---|
| SRC-ALPHA-001 | alpha | architecture_doc | Platform v2 Messaging Architecture |
| SRC-ALPHA-002 | alpha | adr | ADR-007: Message Broker Selection |
| SRC-ALPHA-003 | alpha | meeting_transcript | Architecture Review Board — Messaging |
| SRC-BETA-001 | beta | implementation_note | Async Job Queue Workaround |
| SRC-NOVA-001 | nova | meeting_transcript | Nova Kickoff — Event Architecture |
| SRC-NOVA-002 | nova | design_doc | Nova Event Platform Requirements |
| SRC-DELTA-001 | delta | architecture_doc | Infrastructure Cost Optimization Plan |
| SRC-DELTA-002 | delta | implementation_note | Backup Removal Implementation |
| SRC-DELTA-003 | delta | postmortem | Database Incident Postmortem — July 2025 |

## Session State Keys
| Key | Type | Default | Purpose |
|---|---|---|---|
| `role` | str | `"admin"` | Current user role for ACL |
| `project_id` | str or None | None | Selected project context |
| `last_query_id` | str or None | None | Query ID from last ask_question |
| `last_brief` | DecisionBrief or None | None | Cached brief for trace drawer |
| `selected_decision_id` | str or None | None | Decision opened in explorer/timeline |
| `evidence_ref` | str or None | None | Source ID for evidence panel |

## Colour Tokens
Document the exact colour scheme from _theme.py:
- Epistemic: fact=#60a5fa (blue), observation=#5eead4 (teal), inference=#fbbf24 (amber), recommendation=#a78bfa (violet)
- Drift: none=#4ade80 (green), low=#facc15 (yellow), medium=#fb923c (orange), high=#f87171 (red)
- Comparison: same=#9ca3af (grey), changed=#f87171 (red), newly_present=#fb923c (orange), unknown=#6b7280 (grey), incomparable=#6b7280 (grey-strike)
- Causal: explicit_causal_link=#818cf8 (deep blue), strong_evidence=#5eead4 (teal), possible_causal_link=#fbbf24 (amber), fact=#60a5fa (blue), none=never render
- Status: active=#4ade80 (green), superseded=#fb923c (orange), reconsidered=#60a5fa (blue)
- Always pair colour with text label (accessibility + projector washout)

## Streamlit Version
- Pinned: `streamlit>=1.37` (required for stable `st.dialog`)
- Installed: `streamlit==1.64.0` (verified 2026-09-28)

## Deferred Features (Roadmap)
- Project Impact Graph (PRD)
- Organizational Trends dashboard (PRD)
- Executive trends view
- Manual correction UI
- Interactive graph visualization
