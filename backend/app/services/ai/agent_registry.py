"""AI Agent registry — maps STEP 4 features to API endpoints."""

from app.agents.shared.llm import is_llm_available
from app.schemas.agent import AgentCapabilitiesResponse, AgentCapability


PERSONALITY_OPTIONS = [
    {"id": "teacher", "label_ko": "선생님형", "description": "체계적 단계별 코칭"},
    {"id": "friend", "label_ko": "친구형", "description": "친근한 격려"},
    {"id": "passion", "label_ko": "열정코치형", "description": "에너지 넘치는 동기부여"},
    {"id": "ceo", "label_ko": "CEO형", "description": "결과 중심 전략 코칭"},
    {"id": "data_analyst", "label_ko": "데이터분석형", "description": "지표 기반 피드백"},
]


def get_personality_label(personality_id: str) -> str:
    """Return Korean label for a coach personality id."""
    for option in PERSONALITY_OPTIONS:
        if option["id"] == personality_id:
            return option["label_ko"]
    return personality_id


def list_agent_capabilities() -> AgentCapabilitiesResponse:
    """Return all STEP 4 AI agent test endpoints."""
    capabilities = [
        AgentCapability(
            id="goal_agent",
            name="Goal Agent",
            description="목표 분석 및 세부 목표 생성",
            endpoint="/api/ai/goal/{goal_id}/analyze",
            method="POST",
        ),
        AgentCapability(
            id="planner_agent",
            name="Planner Agent",
            description="월간/주간/일간 계획 생성",
            endpoint="/api/ai/planner/{goal_id}/generate",
            method="POST",
        ),
        AgentCapability(
            id="growth_dna",
            name="Growth DNA",
            description="사용자 성향·집중시간·패턴 조회",
            endpoint="/api/ai/growth-dna",
            method="GET",
        ),
        AgentCapability(
            id="failure_analyzer",
            name="Failure Analyzer",
            description="실패 원인 분석 + DNA 업데이트",
            endpoint="/api/ai/failure/{mission_id}/analyze",
            method="POST",
        ),
        AgentCapability(
            id="auto_replanner",
            name="Auto Replanner",
            description="실패 후 계획 자동 수정",
            endpoint="/api/ai/replanner/{goal_id}",
            method="POST",
        ),
        AgentCapability(
            id="growth_predictor",
            name="Growth Predictor",
            description="목표 달성 확률 예측",
            endpoint="/api/ai/predictor/{goal_id}",
            method="POST",
        ),
        AgentCapability(
            id="future_simulation",
            name="Future Simulation",
            description="Scenario A/B/C 시뮬레이션",
            endpoint="/api/ai/simulation/{goal_id}",
            method="POST",
        ),
        AgentCapability(
            id="growth_timeline",
            name="Growth Timeline",
            description="성장 타임라인 이벤트 목록",
            endpoint="/api/ai/timeline",
            method="GET",
        ),
        AgentCapability(
            id="growth_story",
            name="Growth Story",
            description="성장 스토리 생성",
            endpoint="/api/ai/timeline/story",
            method="GET",
        ),
        AgentCapability(
            id="smart_recommendation",
            name="Smart Recommendation",
            description="목표·도서·습관 추천",
            endpoint="/api/ai/recommendations",
            method="GET",
        ),
        AgentCapability(
            id="ai_tutor",
            name="AI Tutor Personality",
            description="코치 성격 선택/조회",
            endpoint="/api/ai/personality",
            method="GET/PUT",
        ),
        AgentCapability(
            id="coach_feedback",
            name="Coach Feedback",
            description="성격 기반 AI 코치 피드백",
            endpoint="/api/ai/coach/feedback",
            method="POST",
        ),
    ]
    return AgentCapabilitiesResponse(
        agents=capabilities,
        llm_mode="openai" if is_llm_available() else "mock",
    )
