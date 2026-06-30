"""Build daily / weekly / monthly roadmap from goals, plans, and missions."""

from calendar import monthrange
from datetime import date, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.domain.models.enums import GoalStatus, MissionStatus, PlanType
from app.infrastructure.database.models.goal import Goal
from app.infrastructure.database.models.mission import Mission
from app.infrastructure.database.models.plan import Plan
from app.schemas.period_roadmap import (
    PeriodGoalSummary,
    PeriodRoadmapResponse,
    PeriodSection,
    PeriodTaskItem,
)


class PeriodRoadmapService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_roadmap(self, user_id: int) -> PeriodRoadmapResponse:
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        month_start = today.replace(day=1)
        month_end = today.replace(day=monthrange(today.year, today.month)[1])

        goals = (
            self.db.query(Goal)
            .filter(Goal.user_id == user_id)
            .order_by(Goal.priority.asc(), Goal.end_date.asc())
            .all()
        )
        active_goals = [g for g in goals if g.status == GoalStatus.ACTIVE]

        missions = (
            self.db.query(Mission, Goal.title)
            .join(Goal, Mission.goal_id == Goal.id)
            .filter(Mission.user_id == user_id)
            .order_by(Mission.scheduled_date.asc(), Mission.id.asc())
            .all()
        )

        plans = (
            self.db.query(Plan, Goal.title)
            .join(Goal, Plan.goal_id == Goal.id)
            .filter(Plan.user_id == user_id)
            .order_by(Plan.start_date.asc(), Plan.id.asc())
            .all()
        )

        overall = [
            PeriodGoalSummary(
                id=g.id,
                title=g.title,
                description=g.description,
                progress_rate=self._goal_progress(g.id),
                status=g.status.value,
                end_date=g.end_date.isoformat(),
            )
            for g in goals
            if g.status in (GoalStatus.ACTIVE, GoalStatus.PAUSED)
        ]

        daily_missions = [(m, gt) for m, gt in missions if m.scheduled_date == today]
        weekly_missions = [
            (m, gt) for m, gt in missions if week_start <= m.scheduled_date <= week_end
        ]
        monthly_missions = [
            (m, gt) for m, gt in missions if month_start <= m.scheduled_date <= month_end
        ]

        weekly_plans = [
            (p, gt)
            for p, gt in plans
            if p.plan_type == PlanType.WEEKLY and p.start_date <= week_end and p.end_date >= week_start
        ]
        monthly_plans = [
            (p, gt)
            for p, gt in plans
            if p.plan_type == PlanType.MONTHLY and p.start_date <= month_end and p.end_date >= month_start
        ]

        daily_items = [self._mission_item(m, gt) for m, gt in daily_missions]
        weekly_items = self._plan_items(weekly_plans, "weekly") + [
            self._mission_item(m, gt) for m, gt in weekly_missions
        ]
        monthly_items = self._plan_items(monthly_plans, "monthly") + [
            self._mission_item(m, gt) for m, gt in monthly_missions
        ]

        weekly_items = self._dedupe_items(weekly_items)
        monthly_items = self._dedupe_items(monthly_items)

        daily_template = not daily_items
        weekly_template = not weekly_items
        monthly_template = not monthly_items

        if daily_template:
            daily_items = self._template_daily(active_goals or goals)
        if weekly_template:
            weekly_items = self._template_weekly(active_goals or goals)
        if monthly_template:
            monthly_items = self._template_monthly(active_goals or goals)

        return PeriodRoadmapResponse(
            overall_goals=overall,
            daily=self._section(
                "daily",
                "오늘",
                self._format_daily_label(today),
                daily_items,
                daily_template,
            ),
            weekly=self._section(
                "weekly",
                "이번 주",
                f"{week_start.strftime('%m/%d')} – {week_end.strftime('%m/%d')}",
                weekly_items,
                weekly_template,
            ),
            monthly=self._section(
                "monthly",
                "이번 달",
                today.strftime("%Y년 %m월"),
                monthly_items,
                monthly_template,
            ),
        )

    def _mission_item(self, mission: Mission, goal_title: str) -> PeriodTaskItem:
        return PeriodTaskItem(
            id=f"mission-{mission.id}",
            title=mission.title,
            description=mission.description,
            goal_id=mission.goal_id,
            goal_title=goal_title,
            status=mission.status.value,
            source="mission",
            mission_id=mission.id,
            scheduled_date=mission.scheduled_date.isoformat(),
        )

    def _plan_items(self, rows: list[tuple[Plan, str]], horizon: str) -> list[PeriodTaskItem]:
        items: list[PeriodTaskItem] = []
        for plan, goal_title in rows:
            snippet = (plan.content or "").strip()
            if len(snippet) > 120:
                snippet = snippet[:117] + "..."
            items.append(
                PeriodTaskItem(
                    id=f"plan-{plan.id}",
                    title=plan.title,
                    description=snippet or f"{horizon} 실행 계획",
                    goal_id=plan.goal_id,
                    goal_title=goal_title,
                    status="pending",
                    source="plan",
                    scheduled_date=plan.start_date.isoformat(),
                )
            )
        return items

    def _dedupe_items(self, items: list[PeriodTaskItem]) -> list[PeriodTaskItem]:
        seen: set[str] = set()
        unique: list[PeriodTaskItem] = []
        for item in items:
            key = item.id
            if key in seen:
                continue
            seen.add(key)
            unique.append(item)
        return unique

    def _section(
        self,
        horizon: str,
        label: str,
        period_label: str,
        items: list[PeriodTaskItem],
        is_template: bool,
    ) -> PeriodSection:
        completed = sum(1 for i in items if i.status == "completed")
        total = len(items)
        progress = round(completed / total * 100, 1) if total else 0.0
        return PeriodSection(
            horizon=horizon,
            label=label,
            period_label=period_label,
            total=total,
            completed=completed,
            progress_rate=progress,
            is_template=is_template,
            items=items,
        )

    def _template_daily(self, goals: list[Goal]) -> list[PeriodTaskItem]:
        if not goals:
            return [
                PeriodTaskItem(
                    id="template-d-setup",
                    title="첫 번째 목표 설정하기",
                    description="AI 코치에게 목표를 말하거나 목표 페이지에서 추가하세요",
                    source="template",
                ),
                PeriodTaskItem(
                    id="template-d-coach",
                    title="AI 코치와 5분 대화하기",
                    description="목표를 구체화하고 실행 계획을 요청하세요",
                    source="template",
                ),
                PeriodTaskItem(
                    id="template-d-log",
                    title="오늘의 한 줄 기록 남기기",
                    source="template",
                ),
            ]

        items: list[PeriodTaskItem] = []
        for goal in goals[:3]:
            if goal.status != GoalStatus.ACTIVE:
                continue
            items.append(
                PeriodTaskItem(
                    id=f"template-d-{goal.id}",
                    title=f"「{goal.title}」 오늘 25분 실행",
                    description=goal.description,
                    goal_id=goal.id,
                    goal_title=goal.title,
                    source="goal",
                )
            )
        if not items:
            items.append(
                PeriodTaskItem(
                    id="template-d-active",
                    title="활성 목표를 설정하고 오늘의 1가지 과제 정하기",
                    source="template",
                )
            )
        items.append(
            PeriodTaskItem(
                id="template-d-review",
                title="오늘 진행 상황 점검 및 내일 준비",
                source="template",
            )
        )
        return items[:5]

    def _template_weekly(self, goals: list[Goal]) -> list[PeriodTaskItem]:
        if not goals:
            return [
                PeriodTaskItem(
                    id="template-w-plan",
                    title="이번 주 핵심 목표 1가지 정하기",
                    source="template",
                ),
                PeriodTaskItem(
                    id="template-w-schedule",
                    title="주간 실행 일정 잡기 (월·수·금)",
                    source="template",
                ),
                PeriodTaskItem(
                    id="template-w-review",
                    title="주말 회고 — 잘한 점 / 개선할 점",
                    source="template",
                ),
            ]

        items: list[PeriodTaskItem] = []
        for goal in goals[:2]:
            if goal.status != GoalStatus.ACTIVE:
                continue
            items.extend(
                [
                    PeriodTaskItem(
                        id=f"template-w-{goal.id}-focus",
                        title=f"「{goal.title}」 이번 주 핵심 3가지 정하기",
                        goal_id=goal.id,
                        goal_title=goal.title,
                        source="goal",
                    ),
                    PeriodTaskItem(
                        id=f"template-w-{goal.id}-mid",
                        title=f"「{goal.title}」 중간 점검 (수요일)",
                        goal_id=goal.id,
                        goal_title=goal.title,
                        source="goal",
                    ),
                ]
            )
        items.append(
            PeriodTaskItem(
                id="template-w-retro",
                title="주간 회고 및 다음 주 계획 수정",
                source="template",
            )
        )
        return items[:6]

    def _template_monthly(self, goals: list[Goal]) -> list[PeriodTaskItem]:
        if not goals:
            return [
                PeriodTaskItem(
                    id="template-m-vision",
                    title="이번 달 달성하고 싶은 결과 정의하기",
                    source="template",
                ),
                PeriodTaskItem(
                    id="template-m-milestone",
                    title="월간 마일스톤 2~3개 설정",
                    source="template",
                ),
                PeriodTaskItem(
                    id="template-m-ai",
                    title="AI 계획 생성으로 월·주·일 과제 만들기",
                    source="template",
                ),
            ]

        items: list[PeriodTaskItem] = []
        for goal in goals[:2]:
            if goal.status != GoalStatus.ACTIVE:
                continue
            items.extend(
                [
                    PeriodTaskItem(
                        id=f"template-m-{goal.id}-outcome",
                        title=f"「{goal.title}」 이번 달 최종 결과 정의",
                        description=goal.description,
                        goal_id=goal.id,
                        goal_title=goal.title,
                        source="goal",
                    ),
                    PeriodTaskItem(
                        id=f"template-m-{goal.id}-milestone",
                        title=f"「{goal.title}」 월간 마일스톤 점검",
                        goal_id=goal.id,
                        goal_title=goal.title,
                        source="goal",
                    ),
                ]
            )
        items.append(
            PeriodTaskItem(
                id="template-m-summary",
                title="월말 성과 요약 및 다음 달 방향 설정",
                source="template",
            )
        )
        return items[:6]

    def _goal_progress(self, goal_id: int) -> float:
        total = (
            self.db.query(func.count(Mission.id))
            .filter(Mission.goal_id == goal_id)
            .scalar()
            or 0
        )
        if total == 0:
            return 0.0
        completed = (
            self.db.query(func.count(Mission.id))
            .filter(
                Mission.goal_id == goal_id,
                Mission.status == MissionStatus.COMPLETED,
            )
            .scalar()
            or 0
        )
        return round(completed / total * 100, 1)

    def _format_daily_label(self, today: date) -> str:
        weekdays = ("월", "화", "수", "목", "금", "토", "일")
        return f"{today.strftime('%Y년 %m월 %d일')} ({weekdays[today.weekday()]})"
