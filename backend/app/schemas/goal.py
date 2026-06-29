"""Goal-related API schemas."""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.domain.models.enums import GoalStatus


class GoalCreate(BaseModel):
    """Request body for creating a goal."""

    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(None, max_length=2000)
    priority: int = Field(3, ge=1, le=5)
    start_date: date
    end_date: date


class GoalUpdate(BaseModel):
    """Partial update for a goal."""

    title: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = Field(None, max_length=2000)
    priority: int | None = Field(None, ge=1, le=5)
    status: GoalStatus | None = None
    start_date: date | None = None
    end_date: date | None = None


class GoalResponse(BaseModel):
    """Goal returned to clients with computed progress."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    title: str
    description: str | None
    priority: int
    status: GoalStatus
    start_date: date
    end_date: date
    progress_rate: float = Field(description="0–100, from linked missions")
    created_at: datetime
    updated_at: datetime


class DashboardStats(BaseModel):
    """Aggregated growth metrics for dashboard."""

    progress_rate: float = Field(description="Completed missions / total missions (%)")
    achievement_rate: float = Field(description="Completed goals / total goals (%)")
    growth_score: float
    today_missions_total: int
    today_missions_completed: int
    active_goals: int
