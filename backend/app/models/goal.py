"""
Goal ORM model (STEP 2).

A user-defined objective with target date, priority, and progress tracking.
"""

from datetime import UTC, date, datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Date, DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.connection import Base
from app.domain.models.enums import GoalStatus

if TYPE_CHECKING:
    from app.models.feedback import Feedback
    from app.models.task import Task
    from app.models.user import User
    from app.infrastructure.database.models.execution_log import ExecutionLog
    from app.infrastructure.database.models.mission import Mission
    from app.infrastructure.database.models.plan import Plan


class Goal(Base):
    """User goal with measurable progress and linked tasks."""

    __tablename__ = "goals"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    target_date: Mapped[date] = mapped_column(Date, nullable=False)
    priority: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    status: Mapped[GoalStatus] = mapped_column(
        Enum(GoalStatus),
        default=GoalStatus.ACTIVE,
        nullable=False,
    )
    progress: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    # --- Legacy date range (required by existing goal_service) ---
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)

    # --- Relationships ---
    user: Mapped["User"] = relationship(back_populates="goals")
    tasks: Mapped[list["Task"]] = relationship(
        back_populates="goal",
        cascade="all, delete-orphan",
    )
    feedbacks: Mapped[list["Feedback"]] = relationship(
        back_populates="goal",
        cascade="all, delete-orphan",
    )

    # --- Legacy relationships ---
    plans: Mapped[list["Plan"]] = relationship(
        back_populates="goal",
        cascade="all, delete-orphan",
    )
    missions: Mapped[list["Mission"]] = relationship(
        back_populates="goal",
        cascade="all, delete-orphan",
    )
    execution_logs: Mapped[list["ExecutionLog"]] = relationship(
        back_populates="goal",
        cascade="all, delete-orphan",
    )
