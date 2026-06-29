"""API schemas for AI agent responses."""

from pydantic import BaseModel, Field


class SubGoalResponse(BaseModel):
    title: str
    description: str


class PlanResponse(BaseModel):
    id: int
    plan_type: str
    title: str
    content: str | None
    start_date: str
    end_date: str


class MissionResponse(BaseModel):
    id: int
    title: str
    description: str | None
    scheduled_date: str
    status: str


class GoalAnalysisResponse(BaseModel):
    """Goal Agent only — no plan generation."""

    goal_id: int
    realism_score: float
    realism_analysis: str
    sub_goals: list[SubGoalResponse]
    recommendations: list[str]
    risks: list[str]
    llm_mode: str = Field(description="'openai' or 'mock'")


class GeneratePlanResponse(BaseModel):
    """Full pipeline: analysis + plans + missions + memory update."""

    goal_id: int
    realism_score: float
    realism_analysis: str
    sub_goals: list[SubGoalResponse]
    recommendations: list[str]
    plans: list[PlanResponse]
    missions: list[MissionResponse]
    memory_insight: str
    updated_growth_score: float
    llm_mode: str


class FailureAnalysisResponse(BaseModel):
    mission_id: int
    root_causes: list[str]
    patterns: list[str]
    improvements: list[str]
    summary: str
    llm_mode: str


class CoachFeedbackResponse(BaseModel):
    message: str
    action_items: list[str]
    tone: str
    llm_mode: str


class RecommendationResponse(BaseModel):
    goals: list[str]
    books: list[str]
    skills: list[str]
    habits: list[str]
    llm_mode: str


class ScenarioResponse(BaseModel):
    name: str
    description: str
    achievement_probability: float
    expected_completion_date: str
    required_effort_hours: int


class FutureSimulationResponse(BaseModel):
    goal_id: int
    achievement_probability: float
    expected_completion_date: str
    required_effort_hours: int
    scenarios: list[ScenarioResponse]
    llm_mode: str


class GrowthStoryResponse(BaseModel):
    story: str
    highlights: list[str]
    llm_mode: str


class CoachFeedbackRequest(BaseModel):
    context: str = Field(..., min_length=1, max_length=2000)


class GrowthDNAProfileResponse(BaseModel):
    """Growth DNA profile — user behavior patterns."""

    focus_time: int = Field(description="Daily focus minutes")
    success_patterns: list[str]
    failure_patterns: list[str]
    preferred_feedback_style: str | None
    growth_score: float
    llm_mode: str


class GrowthPredictorResponse(BaseModel):
    """Growth Predictor — achievement probability forecast."""

    goal_id: int
    achievement_probability: float
    confidence_level: str
    key_factors: list[str]
    recommendations: list[str]
    predicted_completion_date: str
    llm_mode: str


class AutoReplanResponse(BaseModel):
    """Auto Replanner — revised plans after failure."""

    goal_id: int
    revision_summary: str
    plans: list[PlanResponse]
    missions: list[MissionResponse]
    memory_insight: str
    updated_growth_score: float
    llm_mode: str


class FailureRecoveryResponse(BaseModel):
    """Failure Analyzer + optional Auto Replanner."""

    mission_id: int
    root_causes: list[str]
    patterns: list[str]
    improvements: list[str]
    summary: str
    dna_updated: bool
    replanned: bool
    replan: AutoReplanResponse | None = None
    llm_mode: str


class PersonalityOption(BaseModel):
    id: str
    label_ko: str
    description: str


class PersonalityResponse(BaseModel):
    current: str
    label_ko: str
    available: list[PersonalityOption]


class PersonalityUpdateRequest(BaseModel):
    personality: str = Field(..., description="teacher | friend | passion | ceo | data_analyst")


class AgentCapability(BaseModel):
    id: str
    name: str
    description: str
    endpoint: str
    method: str


class AgentCapabilitiesResponse(BaseModel):
    agents: list[AgentCapability]
    llm_mode: str
