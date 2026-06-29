"""STEP 3 goal management schemas."""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.domain.models.enums import GoalStatus


class TargetPeriod(BaseModel):
    """
    목표 기간 — 시작일과 종료일.

    예: 2026-01-01 ~ 2026-03-31 (3개월 목표)
    """

    start_date: date = Field(..., description="목표 시작일")
    end_date: date = Field(..., description="목표 종료일")

    @model_validator(mode="after")
    def validate_range(self) -> "TargetPeriod":
        if self.end_date < self.start_date:
            raise ValueError("end_date must be on or after start_date")
        return self


class GoalCreateRequest(BaseModel):
    """POST /goal 요청 body."""

    title: str = Field(..., min_length=1, max_length=200, description="목표 제목")
    description: str | None = Field(None, max_length=2000, description="목표 설명")
    target_period: TargetPeriod = Field(..., description="목표 기간")
    priority: int = Field(3, ge=1, le=5, description="우선순위 (1=최고)")
    progress: float = Field(0.0, ge=0.0, le=100.0, description="진행률 0~100")


class GoalUpdateRequest(BaseModel):
    """PUT /goal/{id} 요청 body — 전체 필드 수정."""

    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(None, max_length=2000)
    target_period: TargetPeriod
    priority: int = Field(..., ge=1, le=5)
    progress: float = Field(..., ge=0.0, le=100.0)
    status: GoalStatus = GoalStatus.ACTIVE


class GoalResponse(BaseModel):
    """목표 응답 — 클라이언트에 반환되는 필드."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    title: str
    description: str | None
    target_period: TargetPeriod
    priority: int
    progress: float = Field(description="진행률 0~100")
    status: GoalStatus
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_orm_goal(cls, goal: "object") -> "GoalResponse":
        """ORM Goal → API 응답 변환."""
        from app.models.goal import Goal as GoalModel

        assert isinstance(goal, GoalModel)
        return cls(
            id=goal.id,
            user_id=goal.user_id,
            title=goal.title,
            description=goal.description,
            target_period=TargetPeriod(start_date=goal.start_date, end_date=goal.end_date),
            priority=goal.priority,
            progress=goal.progress,
            status=goal.status,
            created_at=goal.created_at,
            updated_at=goal.updated_at,
        )
