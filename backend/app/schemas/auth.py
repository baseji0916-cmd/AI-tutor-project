"""Authentication-related API schemas."""

from pydantic import BaseModel, Field


class Token(BaseModel):
    """JWT token returned after successful login."""

    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Decoded JWT payload (internal use)."""

    sub: str = Field(..., description="User ID as string")
