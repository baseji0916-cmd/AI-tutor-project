"""Goal and dashboard API routes."""

from fastapi import APIRouter, Depends, status

from app.api.dependencies import get_current_user, get_goal_service
from app.infrastructure.database.models.user import User
from app.schemas.goal import DashboardStats, GoalCreate, GoalResponse, GoalUpdate
from app.services.goal_service import GoalService

router = APIRouter(tags=["Goals"])


@router.get("/goals", response_model=list[GoalResponse])
def list_goals(
    current_user: User = Depends(get_current_user),
    goal_service: GoalService = Depends(get_goal_service),
) -> list[GoalResponse]:
    """List all goals for the authenticated user."""
    return goal_service.list_goals(current_user.id)


@router.post("/goals", response_model=GoalResponse, status_code=status.HTTP_201_CREATED)
def create_goal(
    data: GoalCreate,
    current_user: User = Depends(get_current_user),
    goal_service: GoalService = Depends(get_goal_service),
) -> GoalResponse:
    """Create a new goal."""
    return goal_service.create_goal(current_user, data)


@router.get("/goals/{goal_id}", response_model=GoalResponse)
def get_goal(
    goal_id: int,
    current_user: User = Depends(get_current_user),
    goal_service: GoalService = Depends(get_goal_service),
) -> GoalResponse:
    """Get a single goal by ID."""
    return goal_service.get_goal(current_user.id, goal_id)


@router.patch("/goals/{goal_id}", response_model=GoalResponse)
def update_goal(
    goal_id: int,
    data: GoalUpdate,
    current_user: User = Depends(get_current_user),
    goal_service: GoalService = Depends(get_goal_service),
) -> GoalResponse:
    """Update goal fields (partial)."""
    return goal_service.update_goal(current_user.id, goal_id, data)


@router.delete("/goals/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_goal(
    goal_id: int,
    current_user: User = Depends(get_current_user),
    goal_service: GoalService = Depends(get_goal_service),
) -> None:
    """Delete a goal."""
    goal_service.delete_goal(current_user.id, goal_id)


@router.get("/dashboard/stats", response_model=DashboardStats)
def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    goal_service: GoalService = Depends(get_goal_service),
) -> DashboardStats:
    """Aggregated growth metrics for the dashboard."""
    return goal_service.get_dashboard_stats(current_user.id)
