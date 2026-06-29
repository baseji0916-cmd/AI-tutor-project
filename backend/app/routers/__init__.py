"""FastAPI routers — HTTP presentation layer."""

from app.routers.health_ai import router as health_ai_router

__all__ = ["health_ai_router"]
