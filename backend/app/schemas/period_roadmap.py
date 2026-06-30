"""Period roadmap schemas — daily / weekly / monthly task structure."""

from pydantic import BaseModel, Field


class PeriodGoalSummary(BaseModel):
    id: int
    title: str
    description: str | None
    progress_rate: float
    status: str
    end_date: str


class PeriodTaskItem(BaseModel):
    id: str
    title: str
    description: str | None = None
    goal_id: int | None = None
    goal_title: str | None = None
    status: str = Field(default="pending", description="pending | completed | failed")
    source: str = Field(description="mission | plan | template | goal")
    mission_id: int | None = None
    scheduled_date: str | None = None


class PeriodSection(BaseModel):
    horizon: str = Field(description="daily | weekly | monthly")
    label: str
    period_label: str
    total: int
    completed: int
    progress_rate: float
    is_template: bool = False
    items: list[PeriodTaskItem]


class PeriodRoadmapResponse(BaseModel):
    overall_goals: list[PeriodGoalSummary]
    daily: PeriodSection
    weekly: PeriodSection
    monthly: PeriodSection
