"""Execution log ORM model — records of task attempts."""

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.connection import Base
from app.domain.models.enums import ExecutionStatus

if TYPE_CHECKING:
    from app.infrastructure.database.models.mission import Mission
    from app.models.goal import Goal
    from app.models.user import User


class ExecutionLog(Base):
    """
    Raw execution record used by Failure Analyzer and Growth DNA learning.

    Created when user completes/fails a mission or logs manual activity.
    """

    __tablename__ = "execution_logs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    goal_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("goals.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    mission_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("missions.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    action_type: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[ExecutionStatus] = mapped_column(Enum(ExecutionStatus), nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    duration_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    logged_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    user: Mapped["User"] = relationship(back_populates="execution_logs")
    goal: Mapped[Optional["Goal"]] = relationship(back_populates="execution_logs")
    mission: Mapped[Optional["Mission"]] = relationship(back_populates="execution_logs")
