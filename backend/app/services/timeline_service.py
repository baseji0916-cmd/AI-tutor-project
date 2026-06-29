"""Timeline application service."""

from sqlalchemy.orm import Session

from app.infrastructure.database.models.timeline_event import TimelineEvent
from app.schemas.timeline import TimelineEventResponse


class TimelineService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_events(self, user_id: int, limit: int = 50) -> list[TimelineEventResponse]:
        events = (
            self.db.query(TimelineEvent)
            .filter(TimelineEvent.user_id == user_id)
            .order_by(TimelineEvent.occurred_at.desc())
            .limit(limit)
            .all()
        )
        return [
            TimelineEventResponse(
                id=e.id,
                event_type=e.event_type.value,
                title=e.title,
                description=e.description,
                occurred_at=e.occurred_at.isoformat(),
            )
            for e in events
        ]

    def events_as_text(self, user_id: int, limit: int = 20) -> str:
        events = self.list_events(user_id, limit)
        return "\n".join(
            f"- [{e.occurred_at[:10]}] {e.title}: {e.description or ''}" for e in events
        )
