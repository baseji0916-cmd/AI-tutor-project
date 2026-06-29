"""
Goal application service — CRUD and progress calculation.

Business rules live here; routes stay thin.
"""

from datetime import UTC, date, datetime

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.domain.models.enums import GoalStatus, MissionStatus, TimelineEventType
from app.infrastructure.database.models.goal import Goal
from app.infrastructure.database.models.growth_dna import GrowthDNA
from app.infrastructure.database.models.mission import Mission
from app.infrastructure.database.models.timeline_event import TimelineEvent
from app.infrastructure.database.models.user import User
from app.schemas.goal import DashboardStats, GoalCreate, GoalResponse, GoalUpdate


class GoalService:
    """Manages goals and computes growth metrics."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def list_goals(self, user_id: int) -> list[GoalResponse]:
        """Return all goals for a user, ordered by priority then date."""
        goals = (
            self.db.query(Goal)
            .filter(Goal.user_id == user_id)
            .order_by(Goal.priority.asc(), Goal.end_date.asc())
            .all()
        )
        return [self._to_response(goal) for goal in goals]

    def get_goal(self, user_id: int, goal_id: int) -> GoalResponse:
        """Fetch a single goal owned by the user."""
        goal = self._get_owned_goal(user_id, goal_id)
        return self._to_response(goal)

    def create_goal(self, user: User, data: GoalCreate) -> GoalResponse:
        """Create a goal and log a timeline event."""
        if data.end_date < data.start_date:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="end_date must be on or after start_date",
            )

        goal = Goal(
            user_id=user.id,
            title=data.title.strip(),
            description=data.description,
            priority=data.priority,
            start_date=data.start_date,
            end_date=data.end_date,
            target_date=data.end_date,
        )
        self.db.add(goal)
        self.db.flush()

        self._add_timeline_event(
            user_id=user.id,
            event_type=TimelineEventType.GOAL_CREATED,
            title=f"목표 생성: {goal.title}",
            description=goal.description,
            metadata_json=f'{{"goal_id": {goal.id}}}',
        )
        self.db.commit()
        self.db.refresh(goal)
        return self._to_response(goal)

    def update_goal(self, user_id: int, goal_id: int, data: GoalUpdate) -> GoalResponse:
        """Update goal fields; logs completion to timeline."""
        goal = self._get_owned_goal(user_id, goal_id)
        update_data = data.model_dump(exclude_unset=True)

        if "start_date" in update_data or "end_date" in update_data:
            start = update_data.get("start_date", goal.start_date)
            end = update_data.get("end_date", goal.end_date)
            if end < start:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="end_date must be on or after start_date",
                )

        previous_status = goal.status
        for field, value in update_data.items():
            setattr(goal, field, value)

        if (
            "status" in update_data
            and goal.status == GoalStatus.COMPLETED
            and previous_status != GoalStatus.COMPLETED
        ):
            self._add_timeline_event(
                user_id=user_id,
                event_type=TimelineEventType.GOAL_COMPLETED,
                title=f"목표 달성: {goal.title}",
                metadata_json=f'{{"goal_id": {goal.id}}}',
            )

        self.db.add(goal)
        self.db.commit()
        self.db.refresh(goal)
        return self._to_response(goal)

    def delete_goal(self, user_id: int, goal_id: int) -> None:
        """Permanently delete a goal and cascade related records."""
        goal = self._get_owned_goal(user_id, goal_id)
        self.db.delete(goal)
        self.db.commit()

    def get_dashboard_stats(self, user_id: int) -> DashboardStats:
        """Compute dashboard metrics from goals, missions, and Growth DNA."""
        today = date.today()

        total_missions = (
            self.db.query(func.count(Mission.id))
            .filter(Mission.user_id == user_id)
            .scalar()
            or 0
        )
        completed_missions = (
            self.db.query(func.count(Mission.id))
            .filter(
                Mission.user_id == user_id,
                Mission.status == MissionStatus.COMPLETED,
            )
            .scalar()
            or 0
        )

        total_goals = (
            self.db.query(func.count(Goal.id)).filter(Goal.user_id == user_id).scalar() or 0
        )
        completed_goals = (
            self.db.query(func.count(Goal.id))
            .filter(Goal.user_id == user_id, Goal.status == GoalStatus.COMPLETED)
            .scalar()
            or 0
        )
        active_goals = (
            self.db.query(func.count(Goal.id))
            .filter(Goal.user_id == user_id, Goal.status == GoalStatus.ACTIVE)
            .scalar()
            or 0
        )

        today_total = (
            self.db.query(func.count(Mission.id))
            .filter(Mission.user_id == user_id, Mission.scheduled_date == today)
            .scalar()
            or 0
        )
        today_completed = (
            self.db.query(func.count(Mission.id))
            .filter(
                Mission.user_id == user_id,
                Mission.scheduled_date == today,
                Mission.status == MissionStatus.COMPLETED,
            )
            .scalar()
            or 0
        )

        dna = self.db.query(GrowthDNA).filter(GrowthDNA.user_id == user_id).first()
        growth_score = dna.growth_score if dna else 0.0

        progress_rate = (
            round(completed_missions / total_missions * 100, 1) if total_missions else 0.0
        )
        achievement_rate = (
            round(completed_goals / total_goals * 100, 1) if total_goals else 0.0
        )

        return DashboardStats(
            progress_rate=progress_rate,
            achievement_rate=achievement_rate,
            growth_score=growth_score,
            today_missions_total=today_total,
            today_missions_completed=today_completed,
            active_goals=active_goals,
        )

    def _get_owned_goal(self, user_id: int, goal_id: int) -> Goal:
        goal = (
            self.db.query(Goal)
            .filter(Goal.id == goal_id, Goal.user_id == user_id)
            .first()
        )
        if not goal:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")
        return goal

    def _compute_progress(self, goal_id: int) -> float:
        total = (
            self.db.query(func.count(Mission.id))
            .filter(Mission.goal_id == goal_id)
            .scalar()
            or 0
        )
        if total == 0:
            return 0.0
        completed = (
            self.db.query(func.count(Mission.id))
            .filter(
                Mission.goal_id == goal_id,
                Mission.status == MissionStatus.COMPLETED,
            )
            .scalar()
            or 0
        )
        return round(completed / total * 100, 1)

    def _to_response(self, goal: Goal) -> GoalResponse:
        return GoalResponse(
            id=goal.id,
            user_id=goal.user_id,
            title=goal.title,
            description=goal.description,
            priority=goal.priority,
            status=goal.status,
            start_date=goal.start_date,
            end_date=goal.end_date,
            progress_rate=self._compute_progress(goal.id),
            created_at=goal.created_at,
            updated_at=goal.updated_at,
        )

    def _add_timeline_event(
        self,
        user_id: int,
        event_type: TimelineEventType,
        title: str,
        description: str | None = None,
        metadata_json: str | None = None,
    ) -> None:
        event = TimelineEvent(
            user_id=user_id,
            event_type=event_type,
            title=title,
            description=description,
            metadata_json=metadata_json,
            occurred_at=datetime.now(UTC),
        )
        self.db.add(event)
