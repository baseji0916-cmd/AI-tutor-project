"""
STEP 3 목표 관리 API.

엔드포인트 (모두 JWT 인증 필요):
  POST   /goal         — 목표 생성
  GET    /goal         — 내 목표 목록
  GET    /goal/{id}    — 목표 상세
  PUT    /goal/{id}    — 목표 수정
  DELETE /goal/{id}    — 목표 삭제
"""

from fastapi import APIRouter, Depends, status

from app.api.dependencies import get_current_user, get_step3_goal_service
from app.models.user import User
from app.schemas.step3_goal import GoalCreateRequest, GoalResponse, GoalUpdateRequest
from app.services.step3_goal_service import Step3GoalService

router = APIRouter(prefix="/goal", tags=["Goals (STEP 3)"])


@router.post("", response_model=GoalResponse, status_code=status.HTTP_201_CREATED)
def create_goal(
    data: GoalCreateRequest,
    current_user: User = Depends(get_current_user),
    goal_service: Step3GoalService = Depends(get_step3_goal_service),
) -> GoalResponse:
    """새 목표를 생성합니다."""
    return goal_service.create_goal(current_user, data)


@router.get("", response_model=list[GoalResponse])
def list_goals(
    current_user: User = Depends(get_current_user),
    goal_service: Step3GoalService = Depends(get_step3_goal_service),
) -> list[GoalResponse]:
    """로그인한 사용자의 모든 목표를 반환합니다."""
    return goal_service.list_goals(current_user.id)


@router.get("/{goal_id}", response_model=GoalResponse)
def get_goal(
    goal_id: int,
    current_user: User = Depends(get_current_user),
    goal_service: Step3GoalService = Depends(get_step3_goal_service),
) -> GoalResponse:
    """특정 목표 하나를 조회합니다."""
    return goal_service.get_goal(current_user.id, goal_id)


@router.put("/{goal_id}", response_model=GoalResponse)
def update_goal(
    goal_id: int,
    data: GoalUpdateRequest,
    current_user: User = Depends(get_current_user),
    goal_service: Step3GoalService = Depends(get_step3_goal_service),
) -> GoalResponse:
    """목표 정보를 전체 수정합니다 (PUT)."""
    return goal_service.update_goal(current_user.id, goal_id, data)


@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_goal(
    goal_id: int,
    current_user: User = Depends(get_current_user),
    goal_service: Step3GoalService = Depends(get_step3_goal_service),
) -> None:
    """목표를 삭제합니다."""
    goal_service.delete_goal(current_user.id, goal_id)
