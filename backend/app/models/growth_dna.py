"""
GrowthDNA ORM model (STEP 2).

One-to-one profile capturing learned user behavior patterns.
Updated over time as the user executes goals and tasks.
"""

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.connection import Base

if TYPE_CHECKING:
    from app.models.user import User


class GrowthDNA(Base):
    """Persistent behavioral profile — one record per user."""

    __tablename__ = "growth_dna"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )
    focus_time: Mapped[int] = mapped_column("focus_time_minutes", Integer, default=0, nullable=False)
    success_pattern: Mapped[Optional[str]] = mapped_column("success_patterns", Text, nullable=True)
    failure_pattern: Mapped[Optional[str]] = mapped_column("failure_patterns", Text, nullable=True)
    preferred_feedback_style: Mapped[Optional[str]] = mapped_column(
        "preferred_feedback",
        Text,
        nullable=True,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    # --- Legacy columns ---
    execution_style: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    growth_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    user: Mapped["User"] = relationship(back_populates="growth_dna")

    @property
    def focus_time_minutes(self) -> int:
        return self.focus_time

    @focus_time_minutes.setter
    def focus_time_minutes(self, value: int) -> None:
        self.focus_time = value

    @property
    def success_patterns(self) -> Optional[str]:
        return self.success_pattern

    @success_patterns.setter
    def success_patterns(self, value: Optional[str]) -> None:
        self.success_pattern = value

    @property
    def failure_patterns(self) -> Optional[str]:
        return self.failure_pattern

    @failure_patterns.setter
    def failure_patterns(self, value: Optional[str]) -> None:
        self.failure_pattern = value

    @property
    def preferred_feedback(self) -> Optional[str]:
        return self.preferred_feedback_style

    @preferred_feedback.setter
    def preferred_feedback(self, value: Optional[str]) -> None:
        self.preferred_feedback_style = value
