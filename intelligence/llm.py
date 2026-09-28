from __future__ import annotations

import logging
import re

from pydantic import BaseModel, ValidationError

from contracts.errors import LLMUnavailableError, ValidationFailedError

from . import llm_cache
from .config import get_settings

_LOG = logging.getLogger("decisionprint.intelligence.llm")
_MAX_ATTEMPTS = 2  # first try + one repair retry
_FENCE_RE = re.compile(r"^\s*```(?:json)?\s*|\s*```\s*$", re.IGNORECASE)


def _extract_json_text(raw: str) -> str:
    """Strip code fences and isolate the outermost JSON object/array."""
    text = _FENCE_RE.sub("", raw.strip())
    starts = [i for i in (text.find("{"), text.find("[")) if i != -1]
    if not starts:
        return text
    start, end = min(starts), max(text.rfind("}"), text.rfind("]"))
    return text[start : end + 1] if end > start else text


def _build_repair_prompt(original: str, error: Exception) -> str:
    return (
        f"{original}\n\n---\nYour previous reply was rejected: {str(error)[:600]}\n"
        "Reply again with ONLY one JSON value matching the schema. "
        "No prose, no code fences."
    )


def _call_provider_openai(prompt: str, settings) -> str:
    from openai import OpenAI
    client = OpenAI(
        api_key=settings.llm_api_key,
        base_url="https://integrate.api.nvidia.com/v1" if "nvidia" in settings.llm_model.lower() or "nim" in settings.llm_provider.lower() else None
    )
    # Using temperature from settings if configured (default to 0.0)
    temp = settings.llm_temperature if hasattr(settings, "llm_temperature") and settings.llm_temperature is not None else 0.0
    response = client.chat.completions.create(
        model=settings.llm_model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temp,
    )
    if not response.choices:
        raise ValueError("Empty response choices")
    return response.choices[0].message.content or ""

def _call_provider(prompt: str, settings) -> str:
    # Basic dispatch for the phase
    if settings.llm_provider.lower() == "openai":
        return _call_provider_openai(prompt, settings)
    
    raise NotImplementedError(f"Unsupported provider: {settings.llm_provider}")


def _complete(prompt: str) -> str:
    """One provider call (temperature from settings); maps every failure to LLMUnavailableError."""
    settings = get_settings()
    if not settings.llm_api_key:
        raise LLMUnavailableError("DP_LLM_API_KEY is not set and no cached response exists")
    try:
        return _call_provider(prompt, settings)  # your Phase 0 provider dispatch
    except LLMUnavailableError:
        raise
    except Exception as exc:  # SDK boundary: providers raise many types
        _LOG.debug("provider failure", exc_info=True)
        raise LLMUnavailableError(f"LLM call failed ({type(exc).__name__})") from exc


def call_llm_json(prompt: str, schema: type[BaseModel], *, cache_key: str | None = None):
    """Return a validated `schema` instance; raises LLMUnavailableError, ValidationFailedError."""
    key = llm_cache.make_cache_key(cache_key, prompt, schema) if cache_key else None
    if key:
        hit = llm_cache.load_cached(key)
        if hit is not None:
            try:
                return schema.model_validate_json(hit)
            except ValidationError:
                _LOG.warning("corrupt cache entry %s treated as a miss", key)
    attempt_prompt, last_error = prompt, None
    for _ in range(_MAX_ATTEMPTS):
        raw = _complete(attempt_prompt)
        try:
            obj = schema.model_validate_json(_extract_json_text(raw))
        except ValueError as exc:  # pydantic.ValidationError subclasses ValueError
            last_error = exc
            attempt_prompt = _build_repair_prompt(prompt, exc)
            continue
        if key:
            llm_cache.store_cached(key, label=cache_key, kind="json",
                                   response=obj.model_dump_json(), schema_name=schema.__name__)
        return obj
    raise ValidationFailedError(f"LLM output failed {schema.__name__} validation") from last_error


def call_llm_text(prompt: str, *, cache_key: str | None = None) -> str:
    """Return validated text response; raises LLMUnavailableError, ValidationFailedError."""
    key = llm_cache.make_cache_key(cache_key, prompt, None) if cache_key else None
    if key:
        hit = llm_cache.load_cached(key)
        if hit is not None:
            return hit
    attempt_prompt, last_error = prompt, None
    for _ in range(_MAX_ATTEMPTS):
        raw = _complete(attempt_prompt)
        text = raw.strip()
        if not text:
            last_error = ValueError("Empty response text")
            attempt_prompt = f"{prompt}\n\n---\nYour previous reply was rejected. Reply with non-empty text."
            continue
        if key:
            llm_cache.store_cached(key, label=cache_key, kind="text", response=text)
        return text
    raise ValidationFailedError("LLM output failed text validation (empty)") from last_error
