"""
GrowthPilot application settings.

Loads environment variables from:
1. `backend/.env`       (local dev default)
2. Project root `.env`  (monorepo standard — non-placeholder values win)

Uses python-dotenv + pydantic-settings for validation.
"""

import os
from functools import lru_cache
from pathlib import Path

from dotenv import dotenv_values, load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

# Path: backend/app/config/settings.py → project root is 3 levels up
BACKEND_DIR = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_DIR.parent

_PLACEHOLDER_KEYS = {"", "your_api_key", "your-openai-api-key-here"}


def _load_env_files() -> None:
    """Load .env files without placeholder values overriding real secrets."""
    load_dotenv(BACKEND_DIR / ".env")

    root_path = PROJECT_ROOT / ".env"
    if not root_path.exists():
        return

    for key, value in dotenv_values(root_path).items():
        if value is None:
            continue
        stripped = value.strip()
        if stripped in _PLACEHOLDER_KEYS:
            continue
        os.environ[key] = stripped


_load_env_files()


class Settings(BaseSettings):
    """Central configuration — reused across FastAPI, services, and LangGraph agents."""

    model_config = SettingsConfigDict(
        env_file=str(BACKEND_DIR / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "GrowthPilot"
    app_env: str = "development"
    debug: bool = True

    # Database
    database_url: str = "sqlite:///./growthpilot.db"

    # JWT
    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7

    # OpenAI
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    openai_timeout_seconds: float = 90.0
    openai_max_retries: int = 2

    # CORS
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    @property
    def cors_origin_list(self) -> list[str]:
        """Normalize origins — Render host vars may omit https://."""
        origins: list[str] = []
        for raw in self.cors_origins.split(","):
            origin = raw.strip()
            if not origin:
                continue
            if not origin.startswith("http"):
                origin = f"https://{origin}"
            origins.append(origin.rstrip("/"))
        return origins

    @property
    def has_openai_api_key(self) -> bool:
        """True when a non-placeholder API key is configured."""
        key = self.openai_api_key.strip()
        return bool(key) and key not in {"your-openai-api-key-here", "your_api_key"}


@lru_cache
def get_settings() -> Settings:
    """Cached settings singleton — safe to inject anywhere in the app."""
    return Settings()


def reload_settings() -> Settings:
    """Clear cache after .env changes (startup / hot reload)."""
    get_settings.cache_clear()
    _load_env_files()
    return get_settings()
