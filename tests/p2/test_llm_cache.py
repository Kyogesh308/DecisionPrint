import json
from pathlib import Path
import pytest
from pydantic import BaseModel

from intelligence import llm_cache

class DummySchema(BaseModel):
    value: int

def test_make_cache_key_changes_with_prompt_and_schema():
    k1 = llm_cache.make_cache_key("l", "p1", DummySchema)
    k2 = llm_cache.make_cache_key("l", "p2", DummySchema)
    k3 = llm_cache.make_cache_key("l", "p1", None)
    k4 = llm_cache.make_cache_key("l", "p1", DummySchema)
    assert k1 != k2
    assert k1 != k3
    assert k1 == k4

def test_make_cache_key_ignores_model_and_provider(monkeypatch):
    k1 = llm_cache.make_cache_key("l", "p", DummySchema)
    monkeypatch.setattr(llm_cache.get_settings(), "llm_model", "different")
    k2 = llm_cache.make_cache_key("l", "p", DummySchema)
    assert k1 == k2

def test_load_cached_falls_back_to_demo_cache(monkeypatch, tmp_path):
    monkeypatch.setattr(llm_cache, "DEMO_CACHE_DIR", tmp_path / "demo_cache")
    demo_dir = tmp_path / "demo_cache"
    demo_dir.mkdir(parents=True)
    
    key = llm_cache.make_cache_key("l", "p", None)
    env = {"format": "1", "response": "hit"}
    (demo_dir / f"{key}.json").write_text(json.dumps(env))
    
    assert llm_cache.load_cached(key) == "hit"

def test_store_cached_failure_does_not_raise(monkeypatch, tmp_path):
    monkeypatch.setattr(llm_cache, "_live_dir", lambda: tmp_path / "read_only")
    
    ro = tmp_path / "read_only"
    ro.mkdir()
    # Make it read-only for the test
    import os, stat
    ro.chmod(stat.S_IREAD)
    
    # This should just log a warning, not crash
    llm_cache.store_cached("key", label="l", kind="text", response="data")
    
    # Restore permissions to allow cleanup
    ro.chmod(stat.S_IWRITE | stat.S_IREAD)
