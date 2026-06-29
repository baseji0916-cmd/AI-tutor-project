"""Deterministic mock outputs when OpenAI API key is not configured."""

from datetime import date, timedelta

from app.agents.shared.schemas import (
    GoalAnalysisOutput,
    MemoryUpdateOutput,
    PlannerOutput,
    PlanOutput,
    DailyMissionOutput,
    SubGoalOutput,
)


def mock_goal_analysis(
    title: str,
    description: str,
    start_date: str,
    end_date: str,
) -> GoalAnalysisOutput:
    """Rule-based goal analysis for dev/test without OpenAI."""
    days = (date.fromisoformat(end_date) - date.fromisoformat(start_date)).days
    score = min(85.0, 50.0 + days / 3)
    if days < 14:
        score = max(30.0, score - 20)

    return GoalAnalysisOutput(
        realism_score=round(score, 1),
        realism_analysis=(
            f"'{title}' 목표는 {days}일 기간 기준으로 "
            f"{'달성 가능성이 높습니다' if score >= 60 else '기간 조정이 필요할 수 있습니다'}."
        ),
        sub_goals=[
            SubGoalOutput(title=f"{title} — 1단계 기초", description="기본 습관 형성"),
            SubGoalOutput(title=f"{title} — 2단계 심화", description="난이도 점진적 상승"),
            SubGoalOutput(title=f"{title} — 3단계 완성", description="최종 목표 달성"),
        ],
        recommendations=[
            "매일 30분 이상 집중 시간을 확보하세요",
            "주간 리뷰로 진행 상황을 점검하세요",
        ],
        risks=["일정이 촉박하면 번아웃 위험"] if days < 30 else [],
    )


def mock_planner_output(
    title: str,
    start_date: str,
    end_date: str,
) -> PlannerOutput:
    """Generate sample plans and 7 daily missions without OpenAI."""
    start = date.fromisoformat(start_date)
    end = date.fromisoformat(end_date)
    week_end = min(start + timedelta(days=6), end)

    missions = [
        DailyMissionOutput(
            title=f"{title} — Day {i + 1}",
            description=f"Day {i + 1} 실습 및 기록",
            scheduled_date=(start + timedelta(days=i)).isoformat(),
        )
        for i in range(7)
        if (start + timedelta(days=i)) <= end
    ]

    return PlannerOutput(
        monthly_plan=PlanOutput(
            plan_type="monthly",
            title=f"{title} 월간 로드맵",
            content=f"1주차: 기초 | 2-3주차: 심화 | 4주차: 마무리 및 복습",
            start_date=start_date,
            end_date=end_date,
        ),
        weekly_plan=PlanOutput(
            plan_type="weekly",
            title=f"{title} 1주차 집중",
            content="월-수: 기초 학습 | 목-금: 실습 | 주말: 복습 및 피드백",
            start_date=start_date,
            end_date=week_end.isoformat(),
        ),
        daily_missions=missions,
    )


def mock_memory_update(realism_score: float, coach_personality: str) -> MemoryUpdateOutput:
    """Mock Growth DNA update."""
    delta = 2.0 if realism_score >= 60 else 0.5
    return MemoryUpdateOutput(
        focus_time_minutes=30,
        failure_patterns=["과도한 목표 설정 시 미루기"],
        success_patterns=["짧은 일일 루틴 유지"],
        execution_style="steady",
        growth_score_delta=delta,
        insight="작은 습관부터 시작하면 성공 확률이 높아집니다.",
    )


def mock_failure_analysis(mission_title: str) -> "FailureAnalysisOutput":
    from app.agents.shared.schemas_extended import FailureAnalysisOutput

    return FailureAnalysisOutput(
        root_causes=["시간 부족", "동기 저하", "목표 난이도 과다"],
        patterns=["주말에 미루는 경향"],
        improvements=["미션을 15분 단위로 쪼개기", "전날 밤 알림 설정"],
        summary=f"'{mission_title}' 미션 실패는 실행 환경보다 계획 밀도 문제일 가능성이 큽니다.",
    )


def mock_coach_feedback(personality: str, context: str) -> "CoachFeedbackOutput":
    from app.agents.shared.schemas_extended import CoachFeedbackOutput

    messages = {
        "teacher": ("체계적으로 다시 시작합시다. 오늘 할 일 하나만 정확히 끝내세요.", "structured"),
        "friend": ("괜찮아! 내일 다시 하면 돼~ 작은 것부터 해보자!", "casual"),
        "passion": ("실패는 성공의 어머니! 🔥 지금 바로 10분만 투자해봐!", "motivational"),
        "data_analyst": ("완료율 42%입니다. 집중 시간 30분 확보 시 +18%p 예상됩니다.", "analytical"),
        "ceo": ("결과가 중요합니다. 우선순위 1개에 집중하고 나머지는 defer하세요.", "strategic"),
        "tsundere": ("…흥, 한 번 실패했다고 포기할 거야? 다시 해.", "tough_love"),
    }
    msg, tone = messages.get(personality, messages["teacher"])
    return CoachFeedbackOutput(message=msg, action_items=["오늘 미션 1개 완료"], tone=tone)


def mock_recommendations() -> "RecommendationOutput":
    from app.agents.shared.schemas_extended import RecommendationOutput

    return RecommendationOutput(
        goals=["아침 루틴 30일 챌린지", "주 3회 독서 습관"],
        books=["아토믹 해빗", "데일 카네기 인간관계론"],
        skills=["시간 관리", "집중력"],
        habits=["매일 10분 journaling", "취침 30분 전 디지털 디톡스"],
    )


def mock_future_simulation(goal_title: str, end_date: str) -> "FutureSimulationOutput":
    from app.agents.shared.schemas_extended import FutureSimulationOutput, ScenarioOutput

    base = date.fromisoformat(end_date)
    return FutureSimulationOutput(
        achievement_probability=68.0,
        expected_completion_date=end_date,
        required_effort_hours=120,
        scenarios=[
            ScenarioOutput(
                name="Scenario A — 현재 페이스 유지",
                description="지금 루틴을 유지할 경우",
                achievement_probability=68.0,
                expected_completion_date=end_date,
                required_effort_hours=120,
            ),
            ScenarioOutput(
                name="Scenario B — 집중 시간 +50%",
                description="일일 집중 45분으로 증가",
                achievement_probability=85.0,
                expected_completion_date=(base - timedelta(days=14)).isoformat(),
                required_effort_hours=90,
            ),
            ScenarioOutput(
                name="Scenario C — 목표 축소",
                description="범위를 70%로 줄일 경우",
                achievement_probability=92.0,
                expected_completion_date=(base - timedelta(days=21)).isoformat(),
                required_effort_hours=70,
            ),
        ],
    )


def mock_growth_story(user_name: str, event_count: int) -> "GrowthStoryOutput":
    from app.agents.shared.schemas_extended import GrowthStoryOutput

    return GrowthStoryOutput(
        story=(
            f"{user_name}님의 성장 여정은 {event_count}개의 기록으로 이어지고 있습니다. "
            "작은 목표부터 시작해 꾸준히 쌓아온 발자취가 눈에 띕니다. "
            "앞으로 AI 코치가 함께 더 높은 곳을 향해 나아갈 것입니다."
        ),
        highlights=["목표 설정", "첫 미션 완료", "Growth DNA 학습 시작"],
    )


def mock_replanner_output(
    goal_title: str,
    start_date: str,
    end_date: str,
    failure_summary: str,
) -> "ReplannerOutput":
    from app.agents.shared.schemas_extended import ReplannerOutput

    base = mock_planner_output(goal_title, start_date, end_date)
    return ReplannerOutput(
        revision_summary=f"실패 원인({failure_summary[:40]}...)을 반영해 미션 난이도를 30% 낮췄습니다.",
        monthly_plan=base.monthly_plan,
        weekly_plan=base.weekly_plan,
        daily_missions=base.daily_missions[:5],
    )


def mock_growth_predictor(
    goal_title: str,
    end_date: str,
    progress_rate: float,
    realism_score: float,
) -> "GrowthPredictorOutput":
    from app.agents.shared.schemas_extended import GrowthPredictorOutput

    prob = min(95.0, max(15.0, realism_score * 0.4 + progress_rate * 0.5))
    confidence = "high" if prob >= 70 else "medium" if prob >= 45 else "low"
    return GrowthPredictorOutput(
        achievement_probability=round(prob, 1),
        confidence_level=confidence,
        key_factors=[
            f"현재 진행률 {progress_rate}%",
            f"목표 현실성 {realism_score}점",
            f"목표: {goal_title}",
        ],
        recommendations=["일일 집중 시간 30분 확보", "주간 리뷰 루틴 추가"],
        predicted_completion_date=end_date,
    )
