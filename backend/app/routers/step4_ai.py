"""
STEP 4 AI Growth Agent test API.

LangGraph Multi-Agent endpoints for development and integration testing.
All routes require JWT authentication unless noted.
"""

from fastapi import APIRouter, Depends, Query

from app.api.dependencies import get_agent_service, get_current_user, get_timeline_service
from app.models.user import User
from app.schemas.agent import (
    AgentCapabilitiesResponse,
    AutoReplanResponse,
    CoachFeedbackRequest,
    CoachFeedbackResponse,
    FailureRecoveryResponse,
    FutureSimulationResponse,
    GeneratePlanResponse,
    GoalAnalysisResponse,
    GrowthDNAProfileResponse,
    GrowthPredictorResponse,
    GrowthStoryResponse,
    PersonalityResponse,
    PersonalityUpdateRequest,
    RecommendationResponse,
)
from app.schemas.mission import MissionStatusUpdate
from app.schemas.timeline import TimelineEventResponse
from app.services.agent_service import AgentService
from app.services.ai.agent_registry import list_agent_capabilities
from app.services.timeline_service import TimelineService

router = APIRouter(prefix="/api/ai", tags=["AI Growth Agents (STEP 4)"])


@router.get("", response_model=AgentCapabilitiesResponse)
def list_capabilities() -> AgentCapabilitiesResponse:
    """List all STEP 4 AI agents and their test endpoints."""
    return list_agent_capabilities()


# --- 1. Goal Agent ---
@router.post("/goal/{goal_id}/analyze", response_model=GoalAnalysisResponse)
def goal_analyze(
    goal_id: int,
    current_user: User = Depends(get_current_user),
    agent_service: AgentService = Depends(get_agent_service),
) -> GoalAnalysisResponse:
    """Goal Agent: 목표 분석 + 세부 목표 생성."""
    return agent_service.analyze_goal(current_user.id, goal_id)


# --- 2. Planner Agent ---
@router.post("/planner/{goal_id}/generate", response_model=GeneratePlanResponse)
def planner_generate(
    goal_id: int,
    current_user: User = Depends(get_current_user),
    agent_service: AgentService = Depends(get_agent_service),
) -> GeneratePlanResponse:
    """Planner Agent: 월간/주간/일간 계획 생성 (LangGraph pipeline)."""
    return agent_service.generate_plan(current_user.id, goal_id)


# --- 3. Growth DNA ---
@router.get("/growth-dna", response_model=GrowthDNAProfileResponse)
def growth_dna(
    current_user: User = Depends(get_current_user),
    agent_service: AgentService = Depends(get_agent_service),
) -> GrowthDNAProfileResponse:
    """Growth DNA: 집중시간, 성공/실패 패턴, 성장 점수."""
    return agent_service.get_growth_dna_profile(current_user.id)


# --- 4. Failure Analyzer ---
@router.post("/failure/{mission_id}/analyze", response_model=FailureRecoveryResponse)
def failure_analyze(
    mission_id: int,
    body: MissionStatusUpdate | None = None,
    auto_replan: bool = Query(False, description="실패 분석 후 Auto Replanner 실행"),
    current_user: User = Depends(get_current_user),
    agent_service: AgentService = Depends(get_agent_service),
) -> FailureRecoveryResponse:
    """Failure Analyzer: 실패 원인 분석 + Growth DNA 업데이트 (+ 선택적 재계획)."""
    notes = body.notes if body else ""
    return agent_service.analyze_failure_and_recover(
        current_user.id,
        mission_id,
        notes or "",
        auto_replan=auto_replan,
    )


# --- 5. Auto Replanner ---
@router.post("/replanner/{goal_id}", response_model=AutoReplanResponse)
def auto_replan(
    goal_id: int,
    current_user: User = Depends(get_current_user),
    agent_service: AgentService = Depends(get_agent_service),
) -> AutoReplanResponse:
    """Auto Replanner: 실패 후 계획 자동 수정 (LangGraph recovery pipeline)."""
    return agent_service.auto_replan(current_user.id, goal_id)


# --- 6. Growth Predictor ---
@router.post("/predictor/{goal_id}", response_model=GrowthPredictorResponse)
def growth_predictor(
    goal_id: int,
    current_user: User = Depends(get_current_user),
    agent_service: AgentService = Depends(get_agent_service),
) -> GrowthPredictorResponse:
    """Growth Predictor: 목표 달성 확률 계산."""
    return agent_service.predict_growth(current_user.id, goal_id)


# --- 7. Future Simulation ---
@router.post("/simulation/{goal_id}", response_model=FutureSimulationResponse)
def future_simulation(
    goal_id: int,
    current_user: User = Depends(get_current_user),
    agent_service: AgentService = Depends(get_agent_service),
) -> FutureSimulationResponse:
    """Future Simulation: Scenario A / B / C."""
    return agent_service.simulate_future(current_user.id, goal_id)


# --- 8. Growth Timeline ---
@router.get("/timeline", response_model=list[TimelineEventResponse])
def growth_timeline(
    current_user: User = Depends(get_current_user),
    timeline_service: TimelineService = Depends(get_timeline_service),
) -> list[TimelineEventResponse]:
    """Growth Timeline: 성장 과정 이벤트 목록."""
    return timeline_service.list_events(current_user.id)


# --- 9. Growth Story ---
@router.get("/timeline/story", response_model=GrowthStoryResponse)
def growth_story(
    current_user: User = Depends(get_current_user),
    agent_service: AgentService = Depends(get_agent_service),
) -> GrowthStoryResponse:
    """Growth Story: 타임라인 기반 성장 스토리 생성."""
    return agent_service.growth_story(current_user)


# --- 10. Smart Recommendation ---
@router.get("/recommendations", response_model=RecommendationResponse)
def smart_recommendations(
    current_user: User = Depends(get_current_user),
    agent_service: AgentService = Depends(get_agent_service),
) -> RecommendationResponse:
    """Smart Recommendation: 추천 목표·도서·습관."""
    return agent_service.get_recommendations(current_user)


# --- 11. AI Tutor Personality + Coach Feedback ---
@router.get("/personality", response_model=PersonalityResponse)
def get_personality(
    current_user: User = Depends(get_current_user),
    agent_service: AgentService = Depends(get_agent_service),
) -> PersonalityResponse:
    """AI Tutor Personality: 현재 코치 성격 조회."""
    return agent_service.get_personality(current_user)


@router.put("/personality", response_model=PersonalityResponse)
def update_personality(
    body: PersonalityUpdateRequest,
    current_user: User = Depends(get_current_user),
    agent_service: AgentService = Depends(get_agent_service),
) -> PersonalityResponse:
    """AI Tutor Personality: 코치 성격 변경 (선생님형/친구형/열정코치형/CEO형/데이터분석형)."""
    return agent_service.set_personality(current_user, body.personality)


@router.post("/coach/feedback", response_model=CoachFeedbackResponse)
def coach_feedback(
    body: CoachFeedbackRequest,
    current_user: User = Depends(get_current_user),
    agent_service: AgentService = Depends(get_agent_service),
) -> CoachFeedbackResponse:
    """Coach Agent: 선택한 성격 기반 AI 피드백."""
    return agent_service.coach_feedback(current_user, body.context)
