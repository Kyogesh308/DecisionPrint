"""
DecisionPrint pipeline runner for evaluation.
In fixture mode: returns a pre-built DecisionBrief from P3's fixture builders.
In live mode: calls P1's facade.ask_question (only when branches are merged).
Mode is controlled by DP_BACKEND env var: "fixture" (default) | "live".
"""
from __future__ import annotations

import logging
import os
from datetime import UTC

from contracts.models import DecisionBrief

logger = logging.getLogger("decisionprint.eval.pipeline")


def run_decisionprint_pipeline(
    question: str,
    *,
    project_id: str = "nova",
    user_role: str = "engineer",
) -> DecisionBrief:
    """
    Run the full DecisionPrint pipeline for a question and return a DecisionBrief.

    In fixture mode (DP_BACKEND=fixture or unset): returns the matching canned brief
    from ui.fixtures.builders. Raises ValueError if no fixture matches.
    In live mode (DP_BACKEND=live): calls facade.ask_question; requires merged branches.
    """
    mode = os.environ.get("DP_BACKEND", "fixture").lower()

    if mode == "live":
        return _run_live(question, project_id=project_id, user_role=user_role)
    else:
        return _run_fixture(question, project_id=project_id)


def _run_live(question: str, *, project_id: str, user_role: str) -> DecisionBrief:
    """
    Call P1's facade. This import fails until branches are merged — that is expected.
    In eval, only call this path after confirming branches have merged.
    """
    try:
        from facade import ask_question  # type: ignore[import]
    except ImportError as exc:
        raise RuntimeError(
            "run_decisionprint_pipeline(live mode) requires merged branches. "
            "Set DP_BACKEND=fixture to run against fixtures instead."
        ) from exc

    return ask_question(user_role=user_role, project_id=project_id, question=question)


def _run_fixture(question: str, *, project_id: str) -> DecisionBrief:
    """
    Return a fixture brief. Matches on project_id and question keywords.
    P3 owns ui.fixtures.builders; this import is read-only.
    """
    try:
        from ui.fixtures.builders import (  # type: ignore[import]
            build_fixture_brief_nova_kafka,
        )
    except ImportError:
        # P3 branch not merged yet — use our own test fixture
        logger.warning(
            "ui.fixtures.builders not available; falling back to inline fixture brief"
        )
        return _inline_fixture_brief(question, project_id)

    # Dispatch by project_id and question keywords
    question_lower = question.lower()
    if project_id == "nova" or any(k in question_lower for k in ("kafka", "nova", "should we")):
        return build_fixture_brief_nova_kafka()

    raise ValueError(
        f"No fixture brief available for project_id='{project_id}' "
        f"and question='{question[:60]}'. "
        "Add a fixture builder in ui/fixtures/builders.py or set DP_BACKEND=live."
    )


def _inline_fixture_brief(question: str, project_id: str) -> DecisionBrief:
    """
    Minimal inline fixture used when ui.fixtures.builders is not yet available.
    Enough to produce metrics; not a real answer.
    """
    from datetime import datetime

    from contracts.enums import EpistemicLabel
    from contracts.models import BriefClaim, ConfidenceBreakdown, SourceRef

    stub_ref = SourceRef(source_id="SRC-ALPHA-001", document_id="doc-alpha-001")

    return DecisionBrief(
        query_id="Q-STUB",
        query=question,
        project_id=project_id,
        answer_summary="[Fixture brief — P3 builders not yet merged]",
        historical_decisions=[
            BriefClaim(
                text="DEC-ALPHA-001: Kafka was rejected due to low consumer count.",
                label=EpistemicLabel.FACT,
                source_refs=[stub_ref],
                memory_ids=["mem-alpha-001"],
            )
        ],
        historical_constraints=[],
        current_constraints=[],
        constraint_differences=[],
        observations=[],
        inferences=[],
        drift=None,
        reconsideration_warranted=False,
        recommendation=BriefClaim(
            text="Review this decision given changed constraints.",
            label=EpistemicLabel.RECOMMENDATION,
            source_refs=[stub_ref],
            memory_ids=["mem-alpha-001"],
        ),
        confidence=ConfidenceBreakdown(extraction=0.5, retrieval=0.5, drift=None, causal=None),
        sources=[stub_ref],
        generated_at=datetime.now(tz=UTC).isoformat(),
    )
