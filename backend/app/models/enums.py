"""Domain enums for STEP 2 database models."""

import enum


class GoalStatus(str, enum.Enum):
    """Lifecycle status of a user goal."""

    ACTIVE = "active"
    COMPLETED = "completed"
    PAUSED = "paused"
    ABANDONED = "abandoned"


class TaskType(str, enum.Enum):
    """Planning horizon for a task."""

    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
