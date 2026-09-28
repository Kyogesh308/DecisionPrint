from __future__ import annotations

from memory import (
    build_memory_trace,
    get_memory_stats,
    list_mental_model_views,
    list_observation_views,
    refresh_mental_models,
    wait_for_consolidation,
)


def test_phase4_observation_and_trace_api():
    trace = build_memory_trace("query-001")
    assert "query-001" in trace["query_id"]
    assert trace["timeline"]

    stats = get_memory_stats()
    assert stats["total_projects"] >= 0

    observations = list_observation_views()
    assert isinstance(observations, list)

    models = refresh_mental_models()
    assert isinstance(models, list)
    assert list_mental_model_views()

    assert wait_for_consolidation(timeout_s=0.1) is True
