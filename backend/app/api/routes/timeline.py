"""Timeline API routes."""

from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_user, get_timeline_service
from app.infrastructure.database.models.user import User
from app.schemas.timeline import TimelineEventResponse
from app.services.timeline_service import TimelineService

router = APIRouter(prefix="/timeline", tags=["Timeline"])


@router.get("", response_model=list[TimelineEventResponse])
def list_timeline(
    current_user: User = Depends(get_current_user),
    timeline_service: TimelineService = Depends(get_timeline_service),
) -> list[TimelineEventResponse]:
    return timeline_service.list_events(current_user.id)
