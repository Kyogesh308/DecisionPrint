import pytest
from pydantic import BaseModel

from contracts.errors import LLMUnavailableError, ValidationFailedError
from intelligence import llm

class DummySchema(BaseModel):
    value: int

def test_call_llm_json_strips_code_fences(monkeypatch):
    monkeypatch.setattr(llm, "_complete", lambda p: '```json\n{"value": 42}\n```\nSome prose')
    obj = llm.call_llm_json("prompt", DummySchema)
    assert obj.value == 42

def test_call_llm_json_retries_once_with_error_in_prompt(monkeypatch):
    calls = []
    def mock_complete(p):
        calls.append(p)
        if len(calls) == 1:
            return "not json"
        return '{"value": 42}'
    monkeypatch.setattr(llm, "_complete", mock_complete)
    obj = llm.call_llm_json("prompt", DummySchema)
    assert obj.value == 42
    assert len(calls) == 2
    assert "rejected" in calls[1]

def test_call_llm_json_raises_validation_failed_after_second_bad_reply(monkeypatch):
    monkeypatch.setattr(llm, "_complete", lambda p: "bad")
    with pytest.raises(ValidationFailedError):
        llm.call_llm_json("prompt", DummySchema)

def test_call_llm_json_does_not_cache_invalid_output(monkeypatch, tmp_path):
    monkeypatch.setattr(llm, "_complete", lambda p: "bad")
    monkeypatch.setattr(llm.get_settings(), "cache_dir", str(tmp_path))
    with pytest.raises(ValidationFailedError):
        llm.call_llm_json("prompt", DummySchema, cache_key="test")
    assert not list((tmp_path / "llm").glob("*.json"))

def test_call_llm_json_cache_hit_makes_no_provider_call(monkeypatch, tmp_path):
    monkeypatch.setattr(llm.get_settings(), "cache_dir", str(tmp_path))
    calls = []
    def mock_complete(p):
        calls.append(p)
        return '{"value": 42}'
    monkeypatch.setattr(llm, "_complete", mock_complete)
    
    llm.call_llm_json("prompt", DummySchema, cache_key="test")
    assert len(calls) == 1
    llm.call_llm_json("prompt", DummySchema, cache_key="test")
    assert len(calls) == 1

def test_call_llm_json_corrupt_cache_entry_is_a_miss(monkeypatch, tmp_path):
    monkeypatch.setattr(llm.get_settings(), "cache_dir", str(tmp_path))
    key = llm.llm_cache.make_cache_key("test", "prompt", DummySchema)
    
    dir_path = tmp_path / "llm"
    dir_path.mkdir(parents=True, exist_ok=True)
    (dir_path / f"{key}.json").write_text("not json")
    
    calls = []
    def mock_complete(p):
        calls.append(p)
        return '{"value": 42}'
    monkeypatch.setattr(llm, "_complete", mock_complete)
    
    llm.call_llm_json("prompt", DummySchema, cache_key="test")
    assert len(calls) == 1

def test_call_llm_json_no_api_key_and_cache_miss_raises_llm_unavailable(monkeypatch):
    monkeypatch.setattr(llm.get_settings(), "llm_api_key", "")
    with pytest.raises(LLMUnavailableError):
        llm.call_llm_json("prompt", DummySchema)

def test_call_llm_json_provider_error_maps_to_llm_unavailable(monkeypatch):
    def mock_complete(p):
        raise ValueError("Secret SDK failure")
    monkeypatch.setattr(llm, "_call_provider", mock_complete)
    with pytest.raises(LLMUnavailableError) as exc:
        llm.call_llm_json("prompt", DummySchema)
    assert "Secret SDK failure" not in str(exc.value)

def test_call_llm_json_cache_key_none_never_touches_disk(monkeypatch, tmp_path):
    monkeypatch.setattr(llm.get_settings(), "cache_dir", str(tmp_path))
    monkeypatch.setattr(llm, "_complete", lambda p: '{"value": 42}')
    llm.call_llm_json("prompt", DummySchema, cache_key=None)
    assert not list((tmp_path / "llm").glob("*.json"))
