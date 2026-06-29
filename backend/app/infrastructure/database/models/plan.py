"""Plan ORM model — monthly/weekly/daily plans linked to goals."""

from datetime import UTC, date, datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Date, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.connection import Base
from app.domain.models.enums import PlanType

if TYPE_CHECKING:
    from app.infrastructure.database.models.mission import Mission
    from app.models.goal import Goal
    from app.models.user import User


class Plan(Base):
    """
    Structured plan for a goal at a given time horizon.

    `content` stores plan details as text/JSON string until AI generates rich structure.
    """

    __tablename__ = "plans"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    goal_id: Mapped[int] = mapped_column(ForeignKey("goals.id", ondelete="CASCADE"), index=True)
    plan_type: Mapped[PlanType] = mapped_column(Enum(PlanType), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    user: Mapped["User"] = relationship(back_populates="plans")
    goal: Mapped["Goal"] = relationship(back_populates="plans")
    missions: Mapped[list["Mission"]] = relationship(back_populates="plan", cascade="all, delete-orphan")
