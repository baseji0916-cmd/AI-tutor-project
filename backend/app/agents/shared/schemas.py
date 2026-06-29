"""
Shared Pydantic models for structured LLM outputs.

Each agent returns one of these models via with_structured_output().
"""

from pydantic import BaseModel, Field


class SubGoalOutput(BaseModel):
    title: str = Field(..., description="Sub-goal title")
    description: str = Field(..., description="What success looks like")


class GoalAnalysisOutput(BaseModel):
    """Goal Agent structured response."""

    realism_score: float = Field(..., ge=0, le=100, description="0-100 realism score")
    realism_analysis: str = Field(..., description="Why this score was assigned")
    sub_goals: list[SubGoalOutput] = Field(default_factory=list, max_length=5)
    recommendations: list[str] = Field(default_factory=list, max_length=5)
    risks: list[str] = Field(default_factory=list, max_length=3)


class PlanOutput(BaseModel):
    plan_type: str = Field(..., description="monthly, weekly, or daily")
    title: str
    content: str
    start_date: str = Field(..., description="ISO date YYYY-MM-DD")
    end_date: str = Field(..., description="ISO date YYYY-MM-DD")


class DailyMissionOutput(BaseModel):
    title: str
    description: str
    scheduled_date: str = Field(..., description="ISO date YYYY-MM-DD")


class PlannerOutput(BaseModel):
    """Planner Agent structured response."""

    monthly_plan: PlanOutput
    weekly_plan: PlanOutput
    daily_missions: list[DailyMissionOutput] = Field(default_factory=list, max_length=14)


class MemoryUpdateOutput(BaseModel):
    """Memory Agent structured response — updates Growth DNA."""

    focus_time_minutes: int = Field(..., ge=0, description="Suggested daily focus minutes")
    failure_patterns: list[str] = Field(default_factory=list)
    success_patterns: list[str] = Field(default_factory=list)
    execution_style: str = Field(..., description="Brief execution style label")
    growth_score_delta: float = Field(..., ge=-10, le=10, description="Score adjustment")
    insight: str = Field(..., description="One-sentence learning insight")
