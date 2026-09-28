# P2 Intelligence Engineer — Notes

## LLM Configuration

| Setting        | Value                          | Rationale                                              |
|----------------|--------------------------------|--------------------------------------------------------|
| Provider       | openai                         | Team choice; SDK handles Nvidia NIM correctly          |
| Model (dev)    | meta/llama-3.1-405b-instruct   | High capability JSON model on Nvidia NIM API           |
| Temperature    | 0                              | Determinism; all extraction prompts use temp=0         |

## Prompt Versioning

- Prompts live in `intelligence/prompts/` as Python modules.
- Filename convention: `<purpose>_v<N>.py` (e.g. `extract_decision_v1.py`, `brief_v1.py`).
- When a prompt changes materially, bump N and update cache keys.
- Cache keys embed the version: `"extract_decision_v1:<source_id>"`.
- Demo cache will be snapshotted to `intelligence/demo_cache/` in Phase 6.

## Cache Strategy

- Disk cache at `$DP_CACHE_DIR/llm/`.
- All demo prompts will be pre-cached before the demo run (Phase 6).
- Cache key = caller-supplied string; auto-derived from SHA-256(prompt) if not supplied.

## Phase Log

| Date | Phase | Notes |
|------|-------|-------|
| 2026-09-28 | 0     | Environment set up; LLM wrapper works; fixtures validated |

## Phase 1 — Drift Engine

Completed. Notes:
- Normalization is entirely deterministic; LLM path (`use_llm_for_semantics=True`) not needed for demo corpus.
- `_effective_value()` prefers `normalized_value` over `value` for comparisons — this means callers should normalize before comparing.
- `ops_capacity` in Nova fixture is absent → UNKNOWN → reduces drift_confidence to 0.75 (3 comparable / 4 reason-linked).
- Kafka/Nova test: score = 1.0 (3 changed / 3 known reason-linked), confidence = 0.75 (3/4), warranted = True.
- GraphQL test: score = 0.0 (reason-linked drivers unchanged), warranted = False.
- All 5 required tests pass; additional 7 edge-case tests pass.

## Phase 2 — Decision Brief Builder

Completed. Notes:
- DecisionBrief and all subcomponents (BriefClaim, ConfidenceBreakdown, etc.) added to contracts.models.
- EpistemicLabel and Role enums implemented.
- The synthesis prompt (brief_v1.py) strictly follows the guidelines, forbidding the LLM from making tech recommendations directly.
- The deterministic fallback handles both malformed LLM JSON and unhandled LLM API outages (MemoryUnavailableError).
- All 19 tests across brief features, epistemic labels, fallbacks, and edge cases pass successfully.

## Phase 3 — Decision Extraction

Completed. Notes:
- Prompt Version: v1 (`extract_decision_v1.py`). Prompt strictly enforces epistemic rules and reason-linking.
- Confidence Threshold: LLM defines `extraction_confidence`. Threshold `LOW_EXTRACTION_CONFIDENCE = 0.60` flags `needs_review=True` but does not drop the decision.
- Cache Key Pattern: `extract_decisions_{source.source_id}_v1`. Cached responses correctly bypass LLM cost in re-runs.
- Tests: All extraction and fallback validation tests pass; sequential ID generation is collision-free within process.

## Phase 4 — Outcomes, Current Context & Causal Classifier

Completed. Notes:
- Prompt Versions: `extract_context_v1`, `extract_outcome_v1`, `classify_causal_v1`
- Context Extraction: Drops unknown constraint keys; `is_reason_linked` is hardcoded to `False`.
- Outcomes: Successfully creates objects with `decision_ids=[]` placeholder.
- Causal Classifier: The Python Evidence Guard enforces `_MIN_EVIDENCE_IDS` counts per label, downgrading any hallucinatory or unsupported assertions to `CausalLabel.NONE`.
- Cache Key Patterns: `extract_context_{source.source_id}_v1`, `extract_outcomes_{source.source_id}_v1`, `classify_causal_{decision_id}_{outcome_id}_v1`.
