"""Mission application service — today's missions and completion tracking."""

from datetime import UTC, date, datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.domain.models.enums import ExecutionStatus, MissionStatus, TimelineEventType
from app.infrastructure.database.models.execution_log import ExecutionLog
from app.infrastructure.database.models.goal import Goal
from app.infrastructure.database.models.mission import Mission
from app.infrastructure.database.models.timeline_event import TimelineEvent
from app.schemas.mission import MissionDetailResponse


class MissionService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_today(self, user_id: int) -> list[MissionDetailResponse]:
        today = date.today()
        return self._list_for_date(user_id, today)

    def list_all(self, user_id: int, limit: int = 50) -> list[MissionDetailResponse]:
        rows = (
            self.db.query(Mission, Goal.title)
            .join(Goal, Mission.goal_id == Goal.id)
            .filter(Mission.user_id == user_id)
            .order_by(Mission.scheduled_date.desc(), Mission.id.desc())
            .limit(limit)
            .all()
        )
        return [self._to_response(m, gt) for m, gt in rows]

    def complete_mission(self, user_id: int, mission_id: int, notes: str | None = None) -> MissionDetailResponse:
        mission, goal_title = self._get_owned(user_id, mission_id)
        mission.status = MissionStatus.COMPLETED
        mission.completed_at = datetime.now(UTC)
        self.db.add(mission)

        self.db.add(
            ExecutionLog(
                user_id=user_id,
                goal_id=mission.goal_id,
                mission_id=mission.id,
                action_type="mission_complete",
                status=ExecutionStatus.SUCCESS,
                notes=notes,
                logged_at=datetime.now(UTC),
            )
        )
        self._add_event(
            user_id,
            TimelineEventType.MISSION_COMPLETED,
            f"미션 완료: {mission.title}",
            notes,
        )
        self.db.commit()
        self.db.refresh(mission)
        return self._to_response(mission, goal_title)

    def fail_mission(self, user_id: int, mission_id: int, notes: str | None = None) -> MissionDetailResponse:
        mission, goal_title = self._get_owned(user_id, mission_id)
        mission.status = MissionStatus.FAILED
        self.db.add(mission)

        self.db.add(
            ExecutionLog(
                user_id=user_id,
                goal_id=mission.goal_id,
                mission_id=mission.id,
                action_type="mission_failed",
                status=ExecutionStatus.FAILURE,
                notes=notes,
                logged_at=datetime.now(UTC),
            )
        )
        self._add_event(
            user_id,
            TimelineEventType.MISSION_FAILED,
            f"미션 실패: {mission.title}",
            notes,
        )
        self.db.commit()
        self.db.refresh(mission)
        return self._to_response(mission, goal_title)

    def _list_for_date(self, user_id: int, target: date) -> list[MissionDetailResponse]:
        rows = (
            self.db.query(Mission, Goal.title)
            .join(Goal, Mission.goal_id == Goal.id)
            .filter(Mission.user_id == user_id, Mission.scheduled_date == target)
            .order_by(Mission.id.asc())
            .all()
        )
        return [self._to_response(m, gt) for m, gt in rows]

    def _get_owned(self, user_id: int, mission_id: int) -> tuple[Mission, str]:
        row = (
            self.db.query(Mission, Goal.title)
            .join(Goal, Mission.goal_id == Goal.id)
            .filter(Mission.id == mission_id, Mission.user_id == user_id)
            .first()
        )
        if not row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mission not found")
        return row[0], row[1]

    def _to_response(self, mission: Mission, goal_title: str) -> MissionDetailResponse:
        return MissionDetailResponse(
            id=mission.id,
            goal_id=mission.goal_id,
            goal_title=goal_title,
            title=mission.title,
            description=mission.description,
            scheduled_date=mission.scheduled_date.isoformat(),
            status=mission.status.value,
            completed_at=mission.completed_at.isoformat() if mission.completed_at else None,
        )

    def _add_event(
        self,
        user_id: int,
        event_type: TimelineEventType,
        title: str,
        description: str | None,
    ) -> None:
        self.db.add(
            TimelineEvent(
                user_id=user_id,
                event_type=event_type,
                title=title,
                description=description,
                occurred_at=datetime.now(UTC),
            )
        )
