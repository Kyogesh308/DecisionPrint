# scripts/p2/smoke_test_llm.py
"""Smoke test: call the LLM, validate a Constraint, confirm cache hit on second run."""
import logging
import time
from pydantic import BaseModel
from intelligence.llm import call_llm_json, call_llm_text

logging.basicConfig(level="DEBUG")

# ── Simple text call ────────────────────────────────────────────────────────
t0 = time.time()
text = call_llm_text(
    "Say exactly: SMOKE_OK",
    cache_key="smoke_text_v1",
)
print(f"Text [{time.time()-t0:.2f}s]: {text!r}")

# ── JSON call validated against Constraint ──────────────────────────────────
from contracts.models import Constraint

prompt = (
    "Return a JSON object representing a Kafka constraint: "
    "key='consumer_count', value=2, is_reason_linked=true."
)
t0 = time.time()
c1: Constraint = call_llm_json(prompt, Constraint, cache_key="smoke_constraint_v1")
print(f"First call  [{time.time()-t0:.2f}s]: {c1}")

t0 = time.time()
c2: Constraint = call_llm_json(prompt, Constraint, cache_key="smoke_constraint_v1")
print(f"Second call [{time.time()-t0:.4f}s]: {c2}  <- should be near-instant (cache hit)")

assert c1 == c2, "Cache must return identical result"
print("\n✓ Smoke test passed")
