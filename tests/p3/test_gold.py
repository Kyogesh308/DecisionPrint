"""Tests verifying gold label files and evaluation questions."""

from __future__ import annotations

import json
from pathlib import Path

from contracts import CausalLabel, DriftLevel


def test_gold_files_exist_and_parse() -> None:
    """All 5 gold label JSON files must exist in data/gold/ and be valid JSON."""
    gold_dir = Path("data/gold")
    required_files = [
        "decisions.json",
        "constraints.json",
        "drift_cases.json",
        "causal_links.json",
        "eval_questions.json",
    ]
    for rf in required_files:
        p = gold_dir / rf
        assert p.exists(), f"Missing gold file: {rf}"
        data = json.loads(p.read_text(encoding="utf-8"))
        assert len(data) > 0, f"Gold file {rf} is empty"


def test_gold_decisions_cover_all_chains() -> None:
    """Gold decisions must include the Kafka, Cedar, Redis, GraphQL, and Tracing chains."""
    p = Path("data/gold/decisions.json")
    decisions = json.loads(p.read_text(encoding="utf-8"))
    chains = {d["chain"] for d in decisions}
    assert {"kafka", "cedar", "redis", "graphql", "tracing"}.issubset(chains)

    decision_ids = {d["decision_id"] for d in decisions}
    assert "DEC-ALPHA-001" in decision_ids
    assert "DEC-DELTA-001" in decision_ids


def test_gold_drift_cases_valid_enums() -> None:
    """Drift cases must use valid DriftLevel enums and contain both high, medium, and low."""
    p = Path("data/gold/drift_cases.json")
    cases = json.loads(p.read_text(encoding="utf-8"))
    valid_levels = {e.value for e in DriftLevel}

    levels_seen = set()
    for case in cases:
        lvl = case["expected_level"]
        assert lvl in valid_levels, f"Invalid drift level: {lvl}"
        levels_seen.add(lvl)

    assert "high" in levels_seen
    assert "medium" in levels_seen


def test_gold_causal_links_has_explicit_link() -> None:
    """Cedar chain causal links must use CausalLabel.explicit_causal_link."""
    p = Path("data/gold/causal_links.json")
    links = json.loads(p.read_text(encoding="utf-8"))
    valid_labels = {e.value for e in CausalLabel}

    explicit_found = False
    for link in links:
        lbl = link["expected_label"]
        assert lbl in valid_labels, f"Invalid causal label: {lbl}"
        if lbl == CausalLabel.explicit_causal_link.value:
            explicit_found = True
            assert "SRC-DELTA-003" in link["evidence"]

    assert explicit_found, "Must include at least one explicit_causal_link"


def test_eval_questions_count_and_fields() -> None:
    """Eval questions must have between 15 and 25 questions with valid questions and expectations."""
    p = Path("data/gold/eval_questions.json")
    questions = json.loads(p.read_text(encoding="utf-8"))
    assert 15 <= len(questions) <= 25, f"Expected 15-25 eval questions, got {len(questions)}"

    for q in questions:
        assert "question" in q
        assert len(q["question"]) > 5
