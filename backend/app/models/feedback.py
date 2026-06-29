"""
Feedback ORM model (STEP 2).

Stores AI or coach feedback linked to a specific goal.
"""

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.connection import Base

if TYPE_CHECKING:
    from app.models.goal import Goal


class Feedback(Base):
    """Feedback entry associated with a goal."""

    __tablename__ = "feedbacks"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    goal_id: Mapped[int] = mapped_column(
        ForeignKey("goals.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    feedback_type: Mapped[str] = mapped_column(String(50), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    goal: Mapped["Goal"] = relationship(back_populates="feedbacks")
