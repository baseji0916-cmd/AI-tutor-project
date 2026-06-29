"""User-related API schemas — separate from ORM to avoid leaking DB details."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.domain.models.enums import CoachPersonality


class UserCreate(BaseModel):
    """Request body for user registration."""

    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_]+$")
    password: str = Field(..., min_length=8, max_length=128)
    full_name: str | None = Field(None, max_length=100)
    coach_personality: CoachPersonality = CoachPersonality.TEACHER


class UserLogin(BaseModel):
    """Request body for login — email + password."""

    email: EmailStr
    password: str = Field(..., min_length=1)


class UserUpdate(BaseModel):
    """Request body for profile updates (partial)."""

    full_name: str | None = Field(None, max_length=100)
    bio: str | None = Field(None, max_length=500)
    coach_personality: CoachPersonality | None = None


class UserResponse(BaseModel):
    """User data returned to clients — never includes password hash."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    username: str
    full_name: str | None
    bio: str | None
    coach_personality: CoachPersonality
    is_active: bool
    created_at: datetime
    updated_at: datetime
