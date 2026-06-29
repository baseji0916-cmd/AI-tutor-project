"""Timeline event ORM model — chronological growth history."""

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.connection import Base
from app.domain.models.enums import TimelineEventType

if TYPE_CHECKING:
    from app.models.user import User


class TimelineEvent(Base):
    """
    Growth timeline entry — populated by Timeline Agent and system events.

    `metadata_json` stores extra context (goal id, scores, etc.) as JSON string.
    """

    __tablename__ = "timeline_events"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    event_type: Mapped[TimelineEventType] = mapped_column(Enum(TimelineEventType), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
        index=True,
    )

    user: Mapped["User"] = relationship(back_populates="timeline_events")
