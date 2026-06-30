"""Local / CI verification script for Render deploy readiness."""

import sys
from pathlib import Path

_BACKEND_ROOT = Path(__file__).resolve().parent.parent
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))

# Direct third-party imports used across the backend (must be installable on Render)
REQUIRED_PACKAGES: list[tuple[str, str]] = [
    ("fastapi", "fastapi"),
    ("uvicorn", "uvicorn"),
    ("sqlalchemy", "sqlalchemy"),
    ("alembic", "alembic"),
    ("dotenv", "python-dotenv"),
    ("openai", "openai"),
    ("pydantic", "pydantic"),
    ("pydantic_settings", "pydantic-settings"),
    ("jose", "python-jose"),
    ("passlib", "passlib"),
    ("langchain_core", "langchain-core"),
    ("langchain_openai", "langchain-openai"),
    ("langgraph", "langgraph"),
]


def _check_imports() -> list[str]:
    errors: list[str] = []
    for module, pip_name in REQUIRED_PACKAGES:
        try:
            __import__(module)
            print(f"[OK] import {module} ({pip_name})")
        except ImportError as exc:
            errors.append(f"Missing {pip_name}: {exc}")
    return errors


def main() -> int:
    errors: list[str] = []

    errors.extend(_check_imports())

    # SQLite + models
    try:
        from app.database.connection import engine
        from app.database.initializer import init_db

        init_db()
        with engine.connect() as conn:
            result = conn.execute(__import__("sqlalchemy").text("SELECT 1")).scalar()
        if result != 1:
            errors.append("SQLite: SELECT 1 failed")
        else:
            print("[OK] SQLite connection + init_db")
    except Exception as exc:
        errors.append(f"SQLite: {exc}")

    # OpenAI (optional — skip if no key)
    try:
        from app.config.settings import get_settings
        from app.services.openai_service import OpenAIService

        get_settings.cache_clear()
        service = OpenAIService()
        if service.is_configured():
            result = service.health_check()
            print(f"[OK] OpenAI connected - model={result.get('model')}")
        else:
            print("[SKIP] OpenAI - no API key (mock mode OK for deploy)")
    except Exception as exc:
        errors.append(f"OpenAI: {exc}")

    # FastAPI app import (loads all routers + LangGraph agents)
    try:
        from app.main import app

        assert app.title
        print(f"[OK] FastAPI app - {app.title}")
    except Exception as exc:
        errors.append(f"FastAPI startup: {exc}")

    if errors:
        print("\n[FAIL] Verification errors:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print("\n[PASS] All verification checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
