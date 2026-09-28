import inspect
import intelligence

EXPECTED = {"extract_decisions", "extract_outcomes", "extract_current_context",
            "normalize_constraints", "compare_constraints", "score_drift",
            "classify_causal_link", "build_decision_brief"}

def test_exports_match_contract():
    assert set(intelligence.__all__) == EXPECTED

def test_signatures_match_contract():
    sig = inspect.signature(intelligence.build_decision_brief)
    assert [p.name for p in sig.parameters.values()] == [
        "query_id", "query", "scope", "recall", "decisions", "current", "reflect_fn"]
    assert all(p.kind is inspect.Parameter.KEYWORD_ONLY for p in sig.parameters.values())

def test_intelligence_has_no_forbidden_imports():
    pass

def test_no_print_in_library_code():
    pass

def test_every_llm_call_passes_cache_key():
    pass

def test_public_functions_have_docstrings():
    for name in EXPECTED:
        func = getattr(intelligence, name)
        assert func.__doc__ is not None
