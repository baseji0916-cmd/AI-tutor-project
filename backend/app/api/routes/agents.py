"""AI Agent API routes — LangGraph pipeline triggers."""

from fastapi import APIRouter, Depends

from app.api.dependencies import get_agent_service, get_current_user
from app.infrastructure.database.models.user import User
from app.schemas.agent import (
    CoachFeedbackRequest,
    CoachFeedbackResponse,
    FailureAnalysisResponse,
    FutureSimulationResponse,
    GeneratePlanResponse,
    GoalAnalysisResponse,
    GrowthStoryResponse,
    RecommendationResponse,
)
from app.schemas.mission import MissionStatusUpdate
from app.services.agent_service import AgentService

router = APIRouter(prefix="/agents", tags=["AI Agents"])


@router.post("/goals/{goal_id}/analyze", response_model=GoalAnalysisResponse)
def analyze_goal(
    goal_id: int,
    current_user: User = Depends(get_current_user),
    agent_service: AgentService = Depends(get_agent_service),
) -> GoalAnalysisResponse:
    return agent_service.analyze_goal(current_user.id, goal_id)


@router.post("/goals/{goal_id}/generate-plan", response_model=GeneratePlanResponse)
def generate_plan(
    goal_id: int,
    current_user: User = Depends(get_current_user),
    agent_service: AgentService = Depends(get_agent_service),
) -> GeneratePlanResponse:
    return agent_service.generate_plan(current_user.id, goal_id)


@router.post("/goals/{goal_id}/simulate", response_model=FutureSimulationResponse)
def simulate_future(
    goal_id: int,
    current_user: User = Depends(get_current_user),
    agent_service: AgentService = Depends(get_agent_service),
) -> FutureSimulationResponse:
    return agent_service.simulate_future(current_user.id, goal_id)


@router.post("/missions/{mission_id}/analyze-failure", response_model=FailureAnalysisResponse)
def analyze_failure(
    mission_id: int,
    body: MissionStatusUpdate | None = None,
    current_user: User = Depends(get_current_user),
    agent_service: AgentService = Depends(get_agent_service),
) -> FailureAnalysisResponse:
    notes = body.notes if body else ""
    return agent_service.analyze_failure(current_user.id, mission_id, notes or "")


@router.post("/coach/feedback", response_model=CoachFeedbackResponse)
def coach_feedback(
    body: CoachFeedbackRequest,
    current_user: User = Depends(get_current_user),
    agent_service: AgentService = Depends(get_agent_service),
) -> CoachFeedbackResponse:
    return agent_service.coach_feedback(current_user, body.context)


@router.get("/recommendations", response_model=RecommendationResponse)
def recommendations(
    current_user: User = Depends(get_current_user),
    agent_service: AgentService = Depends(get_agent_service),
) -> RecommendationResponse:
    return agent_service.get_recommendations(current_user)


@router.get("/timeline/story", response_model=GrowthStoryResponse)
def growth_story(
    current_user: User = Depends(get_current_user),
    agent_service: AgentService = Depends(get_agent_service),
) -> GrowthStoryResponse:
    return agent_service.growth_story(current_user)
