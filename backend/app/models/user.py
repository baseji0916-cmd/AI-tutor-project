"""
User ORM model (STEP 2).

Represents a GrowthPilot account with profile and authentication data.
One user owns many goals and recommendations; has one GrowthDNA profile.
"""

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, DateTime, Enum, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.connection import Base
from app.domain.models.enums import CoachPersonality

if TYPE_CHECKING:
    from app.models.goal import Goal
    from app.models.growth_dna import GrowthDNA
    from app.models.recommendation import Recommendation
    from app.infrastructure.database.models.execution_log import ExecutionLog
    from app.infrastructure.database.models.mission import Mission
    from app.infrastructure.database.models.plan import Plan
    from app.infrastructure.database.models.timeline_event import TimelineEvent


class User(Base):
    """Application user — authentication and profile foundation."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column("hashed_password", String(255), nullable=False)
    occupation: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    health_info: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
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

    # --- Legacy columns (kept for backward compatibility with existing services) ---
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    coach_personality: Mapped[CoachPersonality] = mapped_column(
        Enum(CoachPersonality),
        default=CoachPersonality.TEACHER,
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # --- Relationships (STEP 2) ---
    goals: Mapped[list["Goal"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    growth_dna: Mapped[Optional["GrowthDNA"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        uselist=False,
    )
    recommendations: Mapped[list["Recommendation"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    # --- Legacy relationships (Plan / Mission / Timeline from later steps) ---
    plans: Mapped[list["Plan"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    missions: Mapped[list["Mission"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    execution_logs: Mapped[list["ExecutionLog"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    timeline_events: Mapped[list["TimelineEvent"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    @property
    def hashed_password(self) -> str:
        """Backward-compatible alias used by auth_service."""
        return self.password_hash

    @hashed_password.setter
    def hashed_password(self, value: str) -> None:
        self.password_hash = value

    def __init__(self, **kwargs: object) -> None:
        """Auto-fill name from username/full_name when omitted (legacy callers)."""
        if "name" not in kwargs:
            kwargs["name"] = kwargs.get("full_name") or kwargs.get("username") or ""
        super().__init__(**kwargs)
