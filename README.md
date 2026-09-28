# 🧠 DecisionPrint — Organizational Decision Memory

> **The living memory of your engineering organization's architectural decisions, premise drift, and causal outcomes.**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit 1.64.0](https://img.shields.io/badge/streamlit-1.64.0-FF4B4B.svg)](https://streamlit.io/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Tests](https://img.shields.io/badge/tests-29%20passed-brightgreen.svg)]()

---

## 🎯 The Problem

Engineering organizations suffer from **architectural amnesia**:
1. Decisions made years ago (e.g., rejecting Kafka, scaling Redis, removing backups) persist as sacred dogma even when their original premises have completely changed.
2. Teams reinvent past solutions or blindly repeat past mistakes because postmortems and meeting transcripts are buried in Slack channels and Notion workspaces.
3. Conventional AI tools hallucinate recommendations without grounding them in the organization's unique operational reality.

**DecisionPrint** fixes this by turning historical engineering artifacts into an active, continuously grounded organizational memory powered by Hindsight.

---

## 📖 Technical Deep Dive Article (P3 UI Perspective)

We have authored an in-depth technical story from the perspective of the P3 UI Engineer, detailing how DecisionPrint translates Hindsight's temporal memory into a visual decision engine featuring constraint deltas, zero-dependency SVG primitives, modal evidence drawers, and role-scoped memory boundaries:

- **Markdown Format:** [`article.md`](article.md) — *How I Designed a Decision Memory UI to Expose Premise Drift with Hindsight*
- **PDF Document:** [`article.pdf`](article.pdf) — *Publication-ready PDF Edition*

---

## 🏗️ Architecture

DecisionPrint is cleanly decoupled across three distinct layers, bound strictly by typed contracts:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                             UI LAYER (Streamlit)                            │
│  app.py · 0_Overview · 1_Ask · 2_Current_Projects · 3_Timeline             │
│  4_Decision_Explorer · 5_Memory_Evolution · 6_Outcome_Chain                 │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ calls only
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          FACADE PROTOCOL (Contracts)                        │
│  FacadeProtocol (16 runtime-checked methods) · 26 Pydantic Models · 9 Enums │
└──────────────────────┬───────────────────────────────┬──────────────────────┘
                       │                               │
            DP_BACKEND=fixture              DP_BACKEND=live
                       │                               │
                       ▼                               ▼
┌──────────────────────────────┐        ┌─────────────────────────────────────┐
│    FixtureBackend (Demo)     │        │        LiveBackend (Hindsight)      │
│  Deterministic, reproducible │        │  Long-term facts, temporal recall,  │
│  multi-project mock data     │        │  reflect, and higher-order models   │
└──────────────────────────────┘        └─────────────────────────────────────┘
```

---

## 🚀 Quickstart

### 1. Prerequisites
- Python 3.11 or higher
- Git

### 2. Installation
```bash
# Clone the repository
git clone https://github.com/Kyogesh308/DecisionPrint.git
cd DecisionPrint

# Switch to the feature branch
git checkout feat/p3-data-ui

# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate # Linux/macOS

# Install dependencies and editable package
pip install -r requirements/base.txt -r requirements/p3.txt
pip install -e .

# Configure environment
copy .env.example .env   # DP_BACKEND=fixture
```

### 3. Launch the Application
```bash
streamlit run ui/app.py
```
Open **[http://localhost:8501](http://localhost:8501)** in your browser to launch the DecisionPrint executive dashboard.

---

## 🕹️ The 90-Second Demo Script

| Time | Screen | Action | What is Demonstrated | What Comes from Hindsight Memory |
|---|---|---|---|---|
| **0–15 s** | `0_Overview` | Open page, inspect **"Memory learned from 5 historical projects"** hero metrics (42 facts, 12 observations, 3 mental models). Type *"Kafka"* into search. | Instant discovery of past precedents. | Long-term memory recall of project Alpha's decision `DEC-ALPHA-001` with grounded sources `SRC-ALPHA-001` and `SRC-ALPHA-002`. |
| **15–30 s** | `0_Overview` / `Card` | Expand `DEC-ALPHA-001` card. Click `📄 SRC-ALPHA-001`. | Modal dialog opens with verbatim primary excerpt: *"consumer_count=2, ops team small, no replay needed"*. | Primary source evidence excerpt retrieved from disk archive. |
| **30–45 s** | `0_Overview` | Click "📥 Ingest New Project Document", click "⚡ One-Click Demo: Load Nova Kickoff Transcript", hit "🚀 Ingest Document into DecisionPrint". | Real-time memory update. Counter balloons fly; "Memory Updated: SUCCESS" banner appears with 8 new facts. | Ingest pipeline extracts new active constraints (`consumer_count=15`, `replay_required=true`, `traffic_volume=high`). |
| **45–65 s** | `1_Ask` | Switch to Ask screen. Question pre-filled: *"Should Nova use Kafka for event streaming?"* Click "🧠 Query Memory". | **THE KILLER MOMENT:** Above the fold, two columns display: Historical Decision (`DEC-ALPHA-001`) vs. Constraint Delta table. **DRIFT: HIGH (92.0%)** banner states *"⚠️ RECONSIDERATION WARRANTED"*. Red badges flag `consumer_count: 2 ➔ 15`, `replay_required: false ➔ true`. Click **"🧬 Inspect Memory Trace"** to view modal drawer with Retained Sources, Recalled Memories, and Active Observations. | Temporal recall + premise invalidation + multi-dimensional confidence breakdown. |
| **65–78 s** | `5_Memory_Evolution` | Switch to Memory Evolution. Show Mental Models on top (*"Technology adoption follows organizational readiness"*), filter by topic *"messaging"*. | Visual progression of observation evolution over time (reinforcement across independent projects). | Higher-order knowledge consolidation from individual memories into company heuristics. |
| **78–90 s** | `6_Outcome_Chain` | Switch to Outcome Chain. Select `DEC-DELTA-001` (Cedar chain). Observe 5-step sequence with glowing **EXPLICIT CAUSAL LINK** badge. Click grounding source `SRC-DELTA-003`. | Direct causal audit: proves cost-cutting backup removal directly caused July 2025 outage and data loss. | Causal extraction from incident postmortems linking decisions to outcomes. |

---

## 📚 The Five Decision Chains (Corpus Dataset)

The fictional dataset represents **Northstar Systems**, a fast-growing B2B logistics SaaS company in Austin, TX (~200 engineers, 2024–2026):

1. **Kafka Chain (Alpha ➔ Beta ➔ Nova) — The Demo Chain:**
   - Alpha (2024): Rejected Kafka for RabbitMQ because `consumer_count=2` and ops team was small.
   - Beta (2024): Hit limitations, implemented an async job queue workaround.
   - Nova (2026): Scale reached `consumer_count=15`, replay needed for audit trails, ops team expanded. **Drift: HIGH (92%)**, reconsideration warranted.

2. **Cedar / Backup Chain (Delta) — The Causal Chain:**
   - Delta (2025): Removed automated database backups to save $4,200/month (`DEC-DELTA-001`).
   - Incident (July 2025): Database corruption caused a 6-hour outage and partial data loss.
   - Postmortem: Explicitly attributed the recovery time and loss to `DEC-DELTA-001` (`EXPLICIT_CAUSAL_LINK`).

3. **Redis Scaling Chain (Alpha ➔ Gamma ➔ Nova):**
   - Single Redis instance ➔ 4-node cluster ➔ 20-node deployment as cache hit ratios degraded from 0.85 to 0.72.

4. **GraphQL Rejection Chain (Beta ➔ Nova):**
   - Proves *"Drift ≠ Forced Reversal"*: client count grew from 3 to 12, but GraphQL remains rejected due to schema complexity.

5. **Distributed Tracing Chain (Alpha ➔ Beta ➔ Nova):**
   - Logs-only strategy scaled to OpenTelemetry distributed tracing as MTTR targets dropped from 4h to <30m.

---

## 🧪 Verification & Test Suite

The test suite runs 29 automated tests verifying every layer of the application:

```bash
# Run full unit and smoke test suite
pytest tests/p3/ -v

# Run linter on all codebase paths
ruff check ui data scripts/p3 tests/p3 contracts

# Validate manifest integrity (all 18 documents checked)
python scripts/p3/manifest.py
```

### Test Coverage Highlights:
- `test_adapters.py`: Protocol conformance of `FixtureBackend` across all 16 methods; `ScopeError` enforcement for unauthorized roles; lazy loading of `LiveBackend`.
- `test_fixtures.py`: Verification of drift scores, reason-linked constraints, and the Cedar explicit causal link.
- `test_manifest.py`: Schema validation, format constraints (`SRC-<PROJECT>-<NNN>`), duplicate checks, and missing file detection.
- `test_gold.py`: Verification that all 5 gold label files match contracts and evaluation questions.
- `test_ui_smoke.py`: Streamlit `AppTest` execution across `app.py` and all 7 subpages to guarantee zero runtime exceptions.

---

## 🛡️ Role-Based Access Control (ACL)

DecisionPrint enforces role boundaries directly in the facade layer:
- **`engineer`**: Restricted from viewing confidential projects (e.g., Project Delta's cost-cutting decisions and postmortem). Triggers graceful `ScopeError` notifications in the UI.
- **`project_lead` / `executive` / `admin`**: Full visibility across all historical and current project contexts.

---

## 🗺️ Roadmap & Deferred Capabilities

- [ ] Project Impact Graph visualization
- [ ] Cross-organizational executive trend analytics
- [ ] Interactive Mermaid/D3 DAG renderer for multi-branch outcome graphs
- [ ] Bidirectional synchronization with Jira and GitHub ADR pull requests
