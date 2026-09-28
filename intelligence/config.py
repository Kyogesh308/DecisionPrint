"""
intelligence/config.py

Settings for the intelligence package.
All config is read from DP_* env vars via python-dotenv.
"""

import os
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


class IntelligenceSettings:
    """Read-only view of DP_* env vars relevant to intelligence/."""

    def __init__(self) -> None:
        self.llm_provider: str = os.environ.get("DP_LLM_PROVIDER", "anthropic")
        self.llm_model: str = os.environ.get(
            "DP_LLM_MODEL", "claude-3-5-haiku-20241022"
        )
        self.llm_api_key: str = os.environ.get("DP_LLM_API_KEY", "")
        self.llm_base_url: str = os.environ.get("DP_LLM_BASE_URL", "")
        self.cache_dir: str = os.environ.get("DP_CACHE_DIR", "./var/cache")
        self.log_level: str = os.environ.get("DP_LOG_LEVEL", "INFO")
        temp_val = os.environ.get("DP_LLM_TEMPERATURE")
        self.llm_temperature: float | None = float(temp_val) if temp_val is not None else 0.0


@lru_cache(maxsize=1)
def get_settings() -> IntelligenceSettings:
    """Return the singleton settings object; provider credentials are checked on use."""
    return IntelligenceSettings()
