"""
Agent application service — runs LangGraph and persists results to SQLite.

Bridges AI layer (LangGraph) with infrastructure (SQLAlchemy).
All agents reuse OpenAIService via app.agents.shared.llm.get_chat_model().
"""

import json

from datetime import UTC, date, datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.agents.coach_agent.node import run_coach_agent
from app.agents.future_simulation_agent.node import run_future_simulation_agent
from app.agents.goal_agent.node import run_goal_agent
from app.agents.graph.coach_graph import build_growth_coach_graph
from app.agents.graph.failure_recovery_graph import build_failure_recovery_graph
from app.agents.growth_predictor_agent.node import run_growth_predictor_agent
from app.agents.memory_agent.node import make_memory_load_node
from app.agents.recommendation_agent.node import run_recommendation_agent
from app.agents.reflection_agent.node import run_reflection_agent
from app.agents.timeline_agent.node import run_timeline_agent
from app.agents.shared.llm import is_llm_available
from app.domain.models.enums import CoachPersonality, GoalStatus, MissionStatus, PlanType, TimelineEventType
from app.infrastructure.database.models.execution_log import ExecutionLog
from app.infrastructure.database.models.goal import Goal
from app.infrastructure.database.models.growth_dna import GrowthDNA
from app.infrastructure.database.models.mission import Mission
from app.infrastructure.database.models.plan import Plan
from app.infrastructure.database.models.timeline_event import TimelineEvent
from app.infrastructure.database.models.user import User
from app.schemas.agent import (
    AutoReplanResponse,
    CoachFeedbackResponse,
    FailureAnalysisResponse,
    FailureRecoveryResponse,
    FutureSimulationResponse,
    GeneratePlanResponse,
    GoalAnalysisResponse,
    GrowthDNAProfileResponse,
    GrowthPredictorResponse,
    GrowthStoryResponse,
    MissionResponse,
    PersonalityOption,
    PersonalityResponse,
    PlanResponse,
    RecommendationResponse,
    ScenarioResponse,
    SubGoalResponse,
)
from app.services.ai.agent_registry import PERSONALITY_OPTIONS, get_personality_label
from app.services.goal_service import GoalService
from app.services.timeline_service import TimelineService


class AgentService:
    """Orchestrates LangGraph agents with database read/write."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def analyze_goal(self, user_id: int, goal_id: int) -> GoalAnalysisResponse:
        """Run Goal Agent only (no plan persistence)."""
        goal, user = self._get_goal_and_user(user_id, goal_id)
        state = self._build_initial_state(goal, user)

        # Load memory context then run goal agent
        memory_update = make_memory_load_node(self.db)(state)
        state = {**state, **memory_update}
        result = run_goal_agent(state)

        return GoalAnalysisResponse(
            goal_id=goal.id,
            realism_score=result["realism_score"],
            realism_analysis=result["realism_analysis"],
            sub_goals=[SubGoalResponse(**sg) for sg in result.get("sub_goals", [])],
            recommendations=result.get("recommendations", []),
            risks=result.get("risks", []),
            llm_mode="openai" if is_llm_available() else "mock",
        )

    def generate_plan(self, user_id: int, goal_id: int) -> GeneratePlanResponse:
        """Run full LangGraph pipeline and persist plans + missions."""
        goal, user = self._get_goal_and_user(user_id, goal_id)
        initial_state = self._build_initial_state(goal, user)

        graph = build_growth_coach_graph(self.db)
        final_state = graph.invoke(initial_state)

        if final_state.get("error"):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=final_state["error"],
            )

        plans = self._persist_plans(user_id, goal.id, final_state.get("plans", []))
        missions = self._persist_missions(user_id, goal.id, plans, final_state.get("daily_missions", []))

        self._add_timeline_event(
            user_id,
            TimelineEventType.MILESTONE,
            f"AI 계획 생성: {goal.title}",
            f"월간/주간 계획 및 {len(missions)}개 미션 생성",
        )

        return GeneratePlanResponse(
            goal_id=goal.id,
            realism_score=final_state.get("realism_score", 0.0),
            realism_analysis=final_state.get("realism_analysis", ""),
            sub_goals=[SubGoalResponse(**sg) for sg in final_state.get("sub_goals", [])],
            recommendations=final_state.get("recommendations", []),
            plans=plans,
            missions=missions,
            memory_insight=final_state.get("memory_insight", ""),
            updated_growth_score=final_state.get("updated_growth_score", 0.0),
            llm_mode="openai" if is_llm_available() else "mock",
        )

    def analyze_failure(
        self,
        user_id: int,
        mission_id: int,
        notes: str = "",
    ) -> FailureAnalysisResponse:
        """Reflection Agent: analyze why a mission failed."""
        mission = (
            self.db.query(Mission)
            .filter(Mission.id == mission_id, Mission.user_id == user_id)
            .first()
        )
        if not mission:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mission not found")

        goal = self.db.query(Goal).filter(Goal.id == mission.goal_id).first()
        logs_text = self._execution_logs_as_text(mission_id)
        result = run_reflection_agent(
            mission.title,
            mission.description or "",
            goal.title if goal else "",
            notes,
            logs_text,
        )

        self._update_dna_from_failure(user_id, result)

        self._add_timeline_event(
            user_id,
            TimelineEventType.REFLECTION,
            f"실패 분석: {mission.title}",
            result.summary,
        )

        return FailureAnalysisResponse(
            mission_id=mission_id,
            root_causes=result.root_causes,
            patterns=result.patterns,
            improvements=result.improvements,
            summary=result.summary,
            llm_mode="openai" if is_llm_available() else "mock",
        )

    def coach_feedback(self, user: User, context: str) -> CoachFeedbackResponse:
        """Coach Agent: personality-based feedback."""
        stats = GoalService(self.db).get_dashboard_stats(user.id)
        stats_text = (
            f"progress={stats.progress_rate}%, achievement={stats.achievement_rate}%, "
            f"growth_score={stats.growth_score}"
        )
        result = run_coach_agent(user.coach_personality.value, context, stats_text)
        return CoachFeedbackResponse(
            message=result.message,
            action_items=result.action_items,
            tone=result.tone,
            llm_mode="openai" if is_llm_available() else "mock",
        )

    def get_recommendations(self, user: User) -> RecommendationResponse:
        """Recommendation Agent: smart suggestions."""
        goals = self.db.query(Goal).filter(Goal.user_id == user.id, Goal.status == GoalStatus.ACTIVE).all()
        goals_summary = ", ".join(g.title for g in goals) or "None"
        dna = self.db.query(GrowthDNA).filter(GrowthDNA.user_id == user.id).first()
        dna_summary = f"score={dna.growth_score}" if dna else "new user"
        result = run_recommendation_agent(goals_summary, dna_summary, user.coach_personality.value)
        return RecommendationResponse(
            goals=result.goals,
            books=result.books,
            skills=result.skills,
            habits=result.habits,
            llm_mode="openai" if is_llm_available() else "mock",
        )

    def simulate_future(self, user_id: int, goal_id: int) -> FutureSimulationResponse:
        """Future Simulation Agent: scenarios A/B/C."""
        goal, user = self._get_goal_and_user(user_id, goal_id)
        progress = GoalService(self.db)._compute_progress(goal.id)

        initial_state = self._build_initial_state(goal, user)
        memory_loaded = make_memory_load_node(self.db)(initial_state)
        merged = {**initial_state, **memory_loaded}
        analysis = run_goal_agent(merged)
        realism_score = analysis.get("realism_score", 50.0)

        result = run_future_simulation_agent(
            goal.title,
            goal.start_date.isoformat(),
            goal.end_date.isoformat(),
            progress,
            realism_score,
        )

        return FutureSimulationResponse(
            goal_id=goal.id,
            achievement_probability=result.achievement_probability,
            expected_completion_date=result.expected_completion_date,
            required_effort_hours=result.required_effort_hours,
            scenarios=[
                ScenarioResponse(
                    name=s.name,
                    description=s.description,
                    achievement_probability=s.achievement_probability,
                    expected_completion_date=s.expected_completion_date,
                    required_effort_hours=s.required_effort_hours,
                )
                for s in result.scenarios
            ],
            llm_mode="openai" if is_llm_available() else "mock",
        )

    def growth_story(self, user: User) -> GrowthStoryResponse:
        """Timeline Agent: narrative growth story."""
        events_text = TimelineService(self.db).events_as_text(user.id)
        dna = self.db.query(GrowthDNA).filter(GrowthDNA.user_id == user.id).first()
        score = dna.growth_score if dna else 0.0
        name = user.full_name or user.username
        result = run_timeline_agent(name, events_text, score)
        return GrowthStoryResponse(
            story=result.story,
            highlights=result.highlights,
            llm_mode="openai" if is_llm_available() else "mock",
        )

    def get_growth_dna_profile(self, user_id: int) -> GrowthDNAProfileResponse:
        """Growth DNA — focus time, success/failure patterns."""
        dna = self.db.query(GrowthDNA).filter(GrowthDNA.user_id == user_id).first()
        if not dna:
            return GrowthDNAProfileResponse(
                focus_time=0,
                success_patterns=[],
                failure_patterns=[],
                preferred_feedback_style=None,
                growth_score=0.0,
                llm_mode="openai" if is_llm_available() else "mock",
            )
        return GrowthDNAProfileResponse(
            focus_time=dna.focus_time_minutes,
            success_patterns=self._parse_json_list(dna.success_patterns),
            failure_patterns=self._parse_json_list(dna.failure_patterns),
            preferred_feedback_style=dna.preferred_feedback,
            growth_score=dna.growth_score,
            llm_mode="openai" if is_llm_available() else "mock",
        )

    def predict_growth(self, user_id: int, goal_id: int) -> GrowthPredictorResponse:
        """Growth Predictor — standalone achievement probability."""
        goal, user = self._get_goal_and_user(user_id, goal_id)
        progress = GoalService(self.db)._compute_progress(goal.id)

        initial_state = self._build_initial_state(goal, user)
        memory_loaded = make_memory_load_node(self.db)(initial_state)
        merged = {**initial_state, **memory_loaded}
        analysis = run_goal_agent(merged)
        realism_score = analysis.get("realism_score", 50.0)

        result = run_growth_predictor_agent(
            goal.title,
            goal.start_date.isoformat(),
            goal.end_date.isoformat(),
            progress,
            realism_score,
            merged.get("growth_dna_summary", ""),
            user.coach_personality.value,
        )

        return GrowthPredictorResponse(
            goal_id=goal.id,
            achievement_probability=result.achievement_probability,
            confidence_level=result.confidence_level,
            key_factors=result.key_factors,
            recommendations=result.recommendations,
            predicted_completion_date=result.predicted_completion_date,
            llm_mode="openai" if is_llm_available() else "mock",
        )

    def auto_replan(
        self,
        user_id: int,
        goal_id: int,
        failure_summary: str = "",
        improvements: list[str] | None = None,
    ) -> AutoReplanResponse:
        """Auto Replanner — revise plans after failure (LangGraph pipeline)."""
        goal, user = self._get_goal_and_user(user_id, goal_id)
        improvements = improvements or ["미션 난이도 조정", "일일 목표 축소"]

        existing_plans = self.db.query(Plan).filter(Plan.goal_id == goal_id).all()
        plans_summary = ", ".join(f"{p.plan_type}:{p.title}" for p in existing_plans) or "None"

        initial_state = self._build_initial_state(goal, user)
        initial_state.update(
            {
                "realism_score": 45.0,
                "realism_analysis": failure_summary or "Plan revision after failure",
                "existing_plans_summary": plans_summary,
            }
        )
        memory_loaded = make_memory_load_node(self.db)(initial_state)
        initial_state.update(memory_loaded)

        graph = build_failure_recovery_graph(
            self.db,
            failure_summary or "Execution failure detected",
            improvements,
            "",
        )
        final_state = graph.invoke(initial_state)

        plans = self._persist_plans(user_id, goal.id, final_state.get("plans", []))
        missions = self._persist_missions(
            user_id, goal.id, plans, final_state.get("daily_missions", [])
        )

        self._add_timeline_event(
            user_id,
            TimelineEventType.MILESTONE,
            f"AI 계획 재생성: {goal.title}",
            final_state.get("revision_summary", "Auto replan completed"),
        )

        return AutoReplanResponse(
            goal_id=goal.id,
            revision_summary=final_state.get("revision_summary", ""),
            plans=plans,
            missions=missions,
            memory_insight=final_state.get("memory_insight", ""),
            updated_growth_score=final_state.get("updated_growth_score", 0.0),
            llm_mode="openai" if is_llm_available() else "mock",
        )

    def analyze_failure_and_recover(
        self,
        user_id: int,
        mission_id: int,
        notes: str = "",
        auto_replan: bool = False,
    ) -> FailureRecoveryResponse:
        """
        Failure Analyzer + Growth DNA update + optional Auto Replanner.

        One-shot recovery flow for STEP 4 testing.
        """
        failure = self.analyze_failure(user_id, mission_id, notes)
        dna_updated = True  # analyze_failure already updates DNA

        replan_response = None
        replanned = False
        if auto_replan:
            mission = self.db.query(Mission).filter(Mission.id == mission_id).first()
            if mission and mission.goal_id:
                replan_response = self.auto_replan(
                    user_id,
                    mission.goal_id,
                    failure_summary=failure.summary,
                    improvements=failure.improvements,
                )
                replanned = True

        return FailureRecoveryResponse(
            mission_id=mission_id,
            root_causes=failure.root_causes,
            patterns=failure.patterns,
            improvements=failure.improvements,
            summary=failure.summary,
            dna_updated=dna_updated,
            replanned=replanned,
            replan=replan_response,
            llm_mode=failure.llm_mode,
        )

    def get_personality(self, user: User) -> PersonalityResponse:
        """AI Tutor Personality — current selection and available options."""
        return PersonalityResponse(
            current=user.coach_personality.value,
            label_ko=get_personality_label(user.coach_personality.value),
            available=[PersonalityOption(**opt) for opt in PERSONALITY_OPTIONS],
        )

    def set_personality(self, user: User, personality_id: str) -> PersonalityResponse:
        """Update AI tutor personality."""
        try:
            personality = CoachPersonality(personality_id)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid personality. Choose from: {[p['id'] for p in PERSONALITY_OPTIONS]}",
            ) from exc

        user.coach_personality = personality
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return self.get_personality(user)

    def _get_goal_and_user(self, user_id: int, goal_id: int) -> tuple[Goal, User]:
        goal = (
            self.db.query(Goal)
            .filter(Goal.id == goal_id, Goal.user_id == user_id)
            .first()
        )
        if not goal:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")

        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        return goal, user

    def _build_initial_state(self, goal: Goal, user: User) -> dict:
        return {
            "user_id": user.id,
            "goal_id": goal.id,
            "goal_title": goal.title,
            "goal_description": goal.description or "",
            "start_date": goal.start_date.isoformat(),
            "end_date": goal.end_date.isoformat(),
            "coach_personality": user.coach_personality.value,
        }

    def _persist_plans(
        self,
        user_id: int,
        goal_id: int,
        plan_items: list[dict],
    ) -> list[PlanResponse]:
        """Replace existing plans for goal with newly generated ones."""
        self.db.query(Plan).filter(Plan.goal_id == goal_id).delete()

        saved: list[PlanResponse] = []
        for item in plan_items:
            plan = Plan(
                user_id=user_id,
                goal_id=goal_id,
                plan_type=PlanType(item["plan_type"]),
                title=item["title"],
                content=item.get("content"),
                start_date=date.fromisoformat(item["start_date"]),
                end_date=date.fromisoformat(item["end_date"]),
            )
            self.db.add(plan)
            self.db.flush()
            saved.append(
                PlanResponse(
                    id=plan.id,
                    plan_type=plan.plan_type.value,
                    title=plan.title,
                    content=plan.content,
                    start_date=plan.start_date.isoformat(),
                    end_date=plan.end_date.isoformat(),
                )
            )

        self.db.commit()
        return saved

    def _persist_missions(
        self,
        user_id: int,
        goal_id: int,
        plans: list[PlanResponse],
        mission_items: list[dict],
    ) -> list[MissionResponse]:
        """Replace existing missions for goal with daily missions from Planner Agent."""
        self.db.query(Mission).filter(Mission.goal_id == goal_id).delete()

        daily_plan_id = next((p.id for p in plans if p.plan_type == "daily"), None)
        weekly_plan = next((p for p in plans if p.plan_type == "weekly"), None)
        plan_id = daily_plan_id or (weekly_plan.id if weekly_plan else None)

        saved: list[MissionResponse] = []
        for item in mission_items:
            mission = Mission(
                user_id=user_id,
                goal_id=goal_id,
                plan_id=plan_id,
                title=item["title"],
                description=item.get("description"),
                scheduled_date=date.fromisoformat(item["scheduled_date"]),
                status=MissionStatus.PENDING,
            )
            self.db.add(mission)
            self.db.flush()
            saved.append(
                MissionResponse(
                    id=mission.id,
                    title=mission.title,
                    description=mission.description,
                    scheduled_date=mission.scheduled_date.isoformat(),
                    status=mission.status.value,
                )
            )

        self.db.commit()
        return saved

    def _add_timeline_event(
        self,
        user_id: int,
        event_type: TimelineEventType,
        title: str,
        description: str,
    ) -> None:
        event = TimelineEvent(
            user_id=user_id,
            event_type=event_type,
            title=title,
            description=description,
            occurred_at=datetime.now(UTC),
        )
        self.db.add(event)
        self.db.commit()

    def _execution_logs_as_text(self, mission_id: int) -> str:
        """Format execution logs for Failure Analyzer context."""
        logs = (
            self.db.query(ExecutionLog)
            .filter(ExecutionLog.mission_id == mission_id)
            .order_by(ExecutionLog.logged_at.desc())
            .limit(10)
            .all()
        )
        if not logs:
            return ""
        return "\n".join(
            f"- [{log.logged_at.date()}] {log.action_type} ({log.status.value}): {log.notes or 'no notes'}"
            for log in logs
        )

    def _parse_json_list(self, raw: str | None) -> list[str]:
        if not raw:
            return []
        try:
            parsed = json.loads(raw)
            return parsed if isinstance(parsed, list) else [str(parsed)]
        except json.JSONDecodeError:
            return [raw]

    def _update_dna_from_failure(self, user_id: int, failure_result) -> bool:
        """Merge failure patterns into Growth DNA after reflection."""
        dna = self.db.query(GrowthDNA).filter(GrowthDNA.user_id == user_id).first()
        if not dna:
            return False

        existing = self._parse_json_list(dna.failure_patterns)
        merged = list(dict.fromkeys(existing + failure_result.patterns + failure_result.root_causes))[:10]
        dna.failure_patterns = json.dumps(merged, ensure_ascii=False)
        dna.growth_score = max(0.0, dna.growth_score - 0.5)
        self.db.add(dna)
        self.db.commit()
        return True
