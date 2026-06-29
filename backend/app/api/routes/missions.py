"""Mission API routes."""

from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_user, get_mission_service
from app.infrastructure.database.models.user import User
from app.schemas.mission import MissionDetailResponse, MissionStatusUpdate
from app.services.mission_service import MissionService

router = APIRouter(prefix="/missions", tags=["Missions"])


@router.get("/today", response_model=list[MissionDetailResponse])
def list_today_missions(
    current_user: User = Depends(get_current_user),
    mission_service: MissionService = Depends(get_mission_service),
) -> list[MissionDetailResponse]:
    return mission_service.list_today(current_user.id)


@router.get("", response_model=list[MissionDetailResponse])
def list_missions(
    current_user: User = Depends(get_current_user),
    mission_service: MissionService = Depends(get_mission_service),
) -> list[MissionDetailResponse]:
    return mission_service.list_all(current_user.id)


@router.post("/{mission_id}/complete", response_model=MissionDetailResponse)
def complete_mission(
    mission_id: int,
    body: MissionStatusUpdate | None = None,
    current_user: User = Depends(get_current_user),
    mission_service: MissionService = Depends(get_mission_service),
) -> MissionDetailResponse:
    notes = body.notes if body else None
    return mission_service.complete_mission(current_user.id, mission_id, notes)


@router.post("/{mission_id}/fail", response_model=MissionDetailResponse)
def fail_mission(
    mission_id: int,
    body: MissionStatusUpdate | None = None,
    current_user: User = Depends(get_current_user),
    mission_service: MissionService = Depends(get_mission_service),
) -> MissionDetailResponse:
    notes = body.notes if body else None
    return mission_service.fail_mission(current_user.id, mission_id, notes)
