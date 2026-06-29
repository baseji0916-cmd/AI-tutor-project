"""Mission ORM model — daily actionable tasks ('오늘의 미션')."""

from datetime import UTC, date, datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Date, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.connection import Base
from app.domain.models.enums import MissionStatus

if TYPE_CHECKING:
    from app.infrastructure.database.models.execution_log import ExecutionLog
    from app.infrastructure.database.models.plan import Plan
    from app.models.goal import Goal
    from app.models.user import User


class Mission(Base):
    """Single daily mission tied to a goal (and optionally a plan)."""

    __tablename__ = "missions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    goal_id: Mapped[int] = mapped_column(ForeignKey("goals.id", ondelete="CASCADE"), index=True)
    plan_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("plans.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    scheduled_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    status: Mapped[MissionStatus] = mapped_column(
        Enum(MissionStatus),
        default=MissionStatus.PENDING,
        nullable=False,
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    user: Mapped["User"] = relationship(back_populates="missions")
    goal: Mapped["Goal"] = relationship(back_populates="missions")
    plan: Mapped[Optional["Plan"]] = relationship(back_populates="missions")
    execution_logs: Mapped[list["ExecutionLog"]] = relationship(
        back_populates="mission",
        cascade="all, delete-orphan",
    )
