"""
intelligence/_normalizers.py

Deterministic value normalizers for each canonical constraint key (B.7).
All functions are private — only normalize_value() is used externally (within intelligence/).
"""

import logging
import re

logger = logging.getLogger("decisionprint.intelligence.normalizers")

_WORD_TO_INT: dict[str, int] = {
    "zero": 0,
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "eleven": 11,
    "twelve": 12,
    "thirteen": 13,
    "fourteen": 14,
    "fifteen": 15,
    "sixteen": 16,
    "seventeen": 17,
    "eighteen": 18,
    "nineteen": 19,
    "twenty": 20,
}


def _to_int(raw: object) -> int | None:
    """Coerce raw value to int. Returns None if unparseable."""
    if isinstance(raw, bool):
        return None
    if isinstance(raw, int):
        return raw
    if isinstance(raw, float) and raw.is_integer():
        return int(raw)
    if isinstance(raw, str):
        s = raw.strip().lower()
        if s in _WORD_TO_INT:
            return _WORD_TO_INT[s]
        m = re.match(r"~?(\d+)", s)
        if m:
            return int(m.group(1))
    return None


_TRUE_STRINGS = {"yes", "true", "1", "on", "enabled", "required", "yes required"}
_FALSE_STRINGS = {"no", "false", "0", "off", "disabled", "not required", "no replay"}


def _to_bool(raw: object) -> bool | None:
    """Coerce raw value to bool. Returns None if unparseable."""
    if isinstance(raw, bool):
        return raw
    if isinstance(raw, int):
        return bool(raw)
    if isinstance(raw, str):
        s = raw.strip().lower()
        if s in _TRUE_STRINGS:
            return True
        if s in _FALSE_STRINGS:
            return False
    return None


def _normalize_traffic_volume(raw: object) -> str | None:
    s = str(raw).strip().lower()
    if s in {"low", "light", "minimal", "quiet"}:
        return "low"
    if s in {"moderate", "medium", "mid", "average", "normal"}:
        return "moderate"
    if s in {"high", "heavy", "large", "peak", "very high"}:
        return "high"
    return None


def _normalize_ops_capacity(raw: object) -> str | None:
    s = str(raw).strip().lower()
    if s in {"small", "tiny", "minimal", "limited", "lean"}:
        return "small"
    if s in {"medium", "mid", "moderate", "average"}:
        return "medium"
    if s in {"large", "big", "significant", "mature", "dedicated"}:
        return "large"
    return None


def _normalize_client_diversity(raw: object) -> str | None:
    s = str(raw).strip().lower()
    if s in {"internal_only", "internal", "internal only"}:
        return "internal_only"
    if s in {"few_known", "few known", "known", "limited"}:
        return "few_known"
    if s in {"partner", "partners", "b2b"}:
        return "partner"
    if s in {"public", "external", "open", "anyone"}:
        return "public"
    return None


def _normalize_sla_tier(raw: object) -> str | None:
    s = str(raw).strip().lower()
    if s in {"none", "no sla", "best effort", "best-effort"}:
        return "none"
    if s in {"standard", "normal", "basic"}:
        return "standard"
    if s in {"high", "strict", "premium", "99.9", "four nines"}:
        return "high"
    return None


def _normalize_backup_policy(raw: object) -> str | None:
    s = str(raw).strip().lower()
    if s in {"none", "no backup", "no backups", "disabled"}:
        return "none"
    if s in {"manual", "manual backup", "manual backups"}:
        return "manual"
    if s in {"automated", "automatic", "auto", "scheduled"}:
        return "automated"
    return None


def _normalize_observability_maturity(raw: object) -> str | None:
    s = str(raw).strip().lower()
    if s in {"logs_only", "logs only", "logging only", "logs"}:
        return "logs_only"
    if s in {"metrics", "metrics and logs", "logs and metrics"}:
        return "metrics"
    if s in {"tracing", "distributed tracing", "full observability", "traces"}:
        return "tracing"
    return None


def _normalize_budget_pressure(raw: object) -> str | None:
    s = str(raw).strip().lower()
    if s in {"low", "minimal", "relaxed", "ample"}:
        return "low"
    if s in {"medium", "moderate", "normal"}:
        return "medium"
    if s in {"high", "tight", "constrained", "critical"}:
        return "high"
    return None


_INT_KEYS = {
    "consumer_count",
    "instance_count",
    "client_count",
    "service_count",
    "region_count",
}
_BOOL_KEYS = {"replay_required", "async_workflows"}

_CATEGORY_NORMALIZERS: dict[str, object] = {
    "traffic_volume": _normalize_traffic_volume,
    "ops_capacity": _normalize_ops_capacity,
    "client_diversity": _normalize_client_diversity,
    "sla_tier": _normalize_sla_tier,
    "backup_policy": _normalize_backup_policy,
    "observability_maturity": _normalize_observability_maturity,
    "budget_pressure": _normalize_budget_pressure,
}

KNOWN_KEYS: frozenset[str] = frozenset(
    _INT_KEYS | _BOOL_KEYS | _CATEGORY_NORMALIZERS.keys()
)


def normalize_value(key: str, raw_value: object) -> object | None:
    """Normalize a single constraint value for the given canonical key."""
    if key in _INT_KEYS:
        result = _to_int(raw_value)
        if result is None:
            logger.debug(
                "normalize_value: could not parse int for key=%r value=%r",
                key,
                raw_value,
            )
        return result

    if key in _BOOL_KEYS:
        result = _to_bool(raw_value)
        if result is None:
            logger.debug(
                "normalize_value: could not parse bool for key=%r value=%r",
                key,
                raw_value,
            )
        return result

    if key in _CATEGORY_NORMALIZERS:
        normalizer = _CATEGORY_NORMALIZERS[key]
        result = normalizer(raw_value)  # type: ignore[operator]
        if result is None:
            logger.debug(
                "normalize_value: no category match for key=%r value=%r", key, raw_value
            )
        return result

    logger.debug("normalize_value: unknown key=%r — leaving raw", key)
    return None
