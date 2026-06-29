"""Pydantic schemas for STEP 2 database entities."""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.domain.models.enums import GoalStatus
from app.models.enums import TaskType


class UserDBSchema(BaseModel):
    """User entity schema for repository layer."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr
    occupation: str | None = None
    health_info: str | None = None
    created_at: datetime
    updated_at: datetime


class GoalDBSchema(BaseModel):
    """Goal entity schema."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    title: str
    description: str | None = None
    target_date: date
    priority: int = Field(ge=1, le=5)
    status: GoalStatus
    progress: float = Field(ge=0.0, le=100.0)
    created_at: datetime
    updated_at: datetime


class TaskDBSchema(BaseModel):
    """Task entity schema."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    goal_id: int
    title: str
    description: str | None = None
    due_date: date
    task_type: TaskType
    completed: bool
    created_at: datetime
    updated_at: datetime


class GrowthDNADBSchema(BaseModel):
    """GrowthDNA entity schema."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    focus_time: int
    success_pattern: str | None = None
    failure_pattern: str | None = None
    preferred_feedback_style: str | None = None
    updated_at: datetime


class FeedbackDBSchema(BaseModel):
    """Feedback entity schema."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    goal_id: int
    feedback_type: str
    content: str
    created_at: datetime


class RecommendationDBSchema(BaseModel):
    """Recommendation entity schema."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    category: str
    title: str
    description: str | None = None
    created_at: datetime
