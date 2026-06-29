"""Local / CI verification script for STEP 6 final check."""

import sys
from pathlib import Path

# Allow `python scripts/verify_deploy.py` from backend/
_BACKEND_ROOT = Path(__file__).resolve().parent.parent
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))


def main() -> int:
    errors: list[str] = []

    # 1. SQLite + models
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

    # 2. OpenAI (optional — skip if no key)
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

    # 3. FastAPI app import
    try:
        from app.main import app

        assert app.title
        print(f"[OK] FastAPI app - {app.title}")
    except Exception as exc:
        errors.append(f"FastAPI: {exc}")

    if errors:
        print("\n[FAIL] Verification errors:")
        for e in errors:
            print(f"  - {e}")
        return 1

    print("\n[PASS] All verification checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
