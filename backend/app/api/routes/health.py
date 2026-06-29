"""Health check endpoint — used by Render and monitoring."""

from fastapi import APIRouter
from sqlalchemy import text

from app.config.settings import get_settings
from app.core.database import engine

router = APIRouter(tags=["Health"])
settings = get_settings()


@router.get("/health")
def health_check() -> dict[str, str]:
    """
    Liveness probe — API process + SQLite connectivity.

    Render uses this path (/api/v1/health) to confirm the service is alive.
    """
    db_status = "ok"
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception:
        db_status = "error"

    return {
        "status": "healthy" if db_status == "ok" else "degraded",
        "app": settings.app_name,
        "env": settings.app_env,
        "database": db_status,
    }
