"""
GrowthPilot FastAPI application entry point.

Run locally:
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

API docs:
    http://localhost:8000/docs
"""

from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import api_router
from app.config.settings import get_settings, reload_settings
from app.core.database import init_db
from app.routers.health_ai import router as health_ai_router
from app.routers.step4_ai import router as step4_ai_router
from app.routers.step3_auth import router as step3_auth_router
from app.routers.step3_goal import router as step3_goal_router

settings = get_settings()


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """
    Startup / shutdown lifecycle hooks.

    On startup: create DB tables (dev). Step 5 adds Alembic migrations.
    """
    reload_settings()
    init_db()
    yield


app = FastAPI(
    title=settings.app_name,
    description="AI Growth Coach — Multi-Agent backend API",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# CORS — React dev / Vercel / Render static frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_origin_regex=settings.cors_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount all routes under /api/v1 (health is at /api/v1/health)
app.include_router(api_router)

# STEP 4 — AI Growth Agents (LangGraph Multi-Agent)
app.include_router(step4_ai_router)

# STEP 3 — Auth & Goals (spec paths: /auth/*, /goal/*)
app.include_router(step3_auth_router)
app.include_router(step3_goal_router)

# OpenAI health check — GET /api/health/ai
app.include_router(health_ai_router)


@app.get("/", tags=["Root"])
def root() -> dict[str, str]:
    """Root endpoint — quick sanity check without auth."""
    return {
        "message": f"Welcome to {settings.app_name} API",
        "docs": "/docs",
        "health": "/api/v1/health",
        "auth": "/auth/signup",
        "goals": "/goal",
        "ai_agents": "/api/ai",
        "ai_health": "/api/health/ai",
    }
