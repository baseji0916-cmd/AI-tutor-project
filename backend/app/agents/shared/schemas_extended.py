"""Additional structured outputs for Reflection, Coach, Recommendation, Simulation agents."""

from pydantic import BaseModel, Field

from app.agents.shared.schemas import DailyMissionOutput, PlanOutput


class FailureAnalysisOutput(BaseModel):
    root_causes: list[str] = Field(..., max_length=5)
    patterns: list[str] = Field(default_factory=list, max_length=3)
    improvements: list[str] = Field(..., max_length=5)
    summary: str


class CoachFeedbackOutput(BaseModel):
    message: str
    action_items: list[str] = Field(default_factory=list, max_length=3)
    tone: str = Field(..., description="Coaching tone applied")


class RecommendationOutput(BaseModel):
    goals: list[str] = Field(default_factory=list, max_length=3)
    books: list[str] = Field(default_factory=list, max_length=3)
    skills: list[str] = Field(default_factory=list, max_length=3)
    habits: list[str] = Field(default_factory=list, max_length=3)


class ScenarioOutput(BaseModel):
    name: str
    description: str
    achievement_probability: float = Field(..., ge=0, le=100)
    expected_completion_date: str
    required_effort_hours: int = Field(..., ge=0)


class FutureSimulationOutput(BaseModel):
    achievement_probability: float = Field(..., ge=0, le=100)
    expected_completion_date: str
    required_effort_hours: int
    scenarios: list[ScenarioOutput] = Field(..., min_length=3, max_length=3)


class GrowthStoryOutput(BaseModel):
    story: str = Field(..., description="Narrative growth story")
    highlights: list[str] = Field(default_factory=list, max_length=5)


class ReplannerOutput(BaseModel):
    """Auto Replanner — revised plans after failure analysis."""

    revision_summary: str = Field(..., description="Why and how the plan was revised")
    monthly_plan: PlanOutput
    weekly_plan: PlanOutput
    daily_missions: list[DailyMissionOutput] = Field(default_factory=list, max_length=14)


class GrowthPredictorOutput(BaseModel):
    """Growth Predictor — standalone achievement probability."""

    achievement_probability: float = Field(..., ge=0, le=100)
    confidence_level: str = Field(..., description="high | medium | low")
    key_factors: list[str] = Field(default_factory=list, max_length=5)
    recommendations: list[str] = Field(default_factory=list, max_length=5)
    predicted_completion_date: str = Field(..., description="ISO date YYYY-MM-DD")
