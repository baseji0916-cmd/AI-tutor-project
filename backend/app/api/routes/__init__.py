"""Aggregate API routers under /api/v1."""

from fastapi import APIRouter

from app.api.routes import agents, auth, goals, health, missions, timeline

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(goals.router)
api_router.include_router(missions.router)
api_router.include_router(timeline.router)
api_router.include_router(agents.router)
