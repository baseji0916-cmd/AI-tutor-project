"""
STEP 3 goal management service.

Service Layer: 목표 CRUD 비즈니스 규칙.
Repository Pattern: DB 접근은 GoalRepository에 위임.
"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.goal import Goal
from app.models.user import User
from app.repositories.goal_repository import GoalRepository
from app.schemas.step3_goal import GoalCreateRequest, GoalResponse, GoalUpdateRequest


class Step3GoalService:
    """목표 생성·조회·수정·삭제."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.goal_repo = GoalRepository(db)

    def create_goal(self, user: User, data: GoalCreateRequest) -> GoalResponse:
        """새 목표 생성."""
        period = data.target_period
        goal = Goal(
            user_id=user.id,
            title=data.title.strip(),
            description=data.description,
            priority=data.priority,
            progress=data.progress,
            start_date=period.start_date,
            end_date=period.end_date,
            target_date=period.end_date,
        )
        self.goal_repo.add(goal)
        self.goal_repo.commit()
        self.goal_repo.refresh(goal)
        return GoalResponse.from_orm_goal(goal)

    def list_goals(self, user_id: int) -> list[GoalResponse]:
        """내 목표 전체 목록."""
        goals = self.goal_repo.list_by_user(user_id)
        return [GoalResponse.from_orm_goal(g) for g in goals]

    def get_goal(self, user_id: int, goal_id: int) -> GoalResponse:
        """단일 목표 조회 (본인 소유만)."""
        goal = self._get_owned_goal(user_id, goal_id)
        return GoalResponse.from_orm_goal(goal)

    def update_goal(
        self,
        user_id: int,
        goal_id: int,
        data: GoalUpdateRequest,
    ) -> GoalResponse:
        """목표 전체 수정 (PUT)."""
        goal = self._get_owned_goal(user_id, goal_id)
        period = data.target_period

        goal.title = data.title.strip()
        goal.description = data.description
        goal.priority = data.priority
        goal.progress = data.progress
        goal.status = data.status
        goal.start_date = period.start_date
        goal.end_date = period.end_date
        goal.target_date = period.end_date

        self.goal_repo.commit()
        self.goal_repo.refresh(goal)
        return GoalResponse.from_orm_goal(goal)

    def delete_goal(self, user_id: int, goal_id: int) -> None:
        """목표 삭제 (연관 Task/Feedback은 DB cascade로 함께 삭제)."""
        goal = self._get_owned_goal(user_id, goal_id)
        self.goal_repo.delete(goal)
        self.goal_repo.commit()

    def _get_owned_goal(self, user_id: int, goal_id: int) -> Goal:
        """본인 목표가 아니면 404."""
        goal = self.goal_repo.get_by_id_and_user(goal_id, user_id)
        if not goal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Goal not found",
            )
        return goal
