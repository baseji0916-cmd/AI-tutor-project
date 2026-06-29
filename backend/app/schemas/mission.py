"""Mission API schemas."""

from pydantic import BaseModel, Field


class MissionDetailResponse(BaseModel):
    id: int
    goal_id: int
    goal_title: str
    title: str
    description: str | None
    scheduled_date: str
    status: str
    completed_at: str | None = None


class MissionStatusUpdate(BaseModel):
    notes: str | None = Field(None, max_length=500)
