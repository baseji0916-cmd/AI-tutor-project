"""Timeline API schemas."""

from pydantic import BaseModel


class TimelineEventResponse(BaseModel):
    id: int
    event_type: str
    title: str
    description: str | None
    occurred_at: str
