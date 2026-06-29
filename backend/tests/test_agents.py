"""LangGraph agent pipeline tests (mock mode — no OpenAI key required)."""

from fastapi.testclient import TestClient

from tests.conftest import create_user_and_goal


def test_goal_analyze_mock(client: TestClient) -> None:
    headers, goal_id = create_user_and_goal(client)
    resp = client.post(f"/api/v1/agents/goals/{goal_id}/analyze", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["llm_mode"] == "mock"
    assert 0 <= data["realism_score"] <= 100
    assert len(data["sub_goals"]) >= 2


def test_generate_plan_persists_missions(client: TestClient) -> None:
    headers, goal_id = create_user_and_goal(client)
    resp = client.post(f"/api/v1/agents/goals/{goal_id}/generate-plan", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["plans"]) == 2
    assert len(data["missions"]) >= 1


def test_coach_graph_invoke_directly() -> None:
    from datetime import date, timedelta

    from app.agents.graph.coach_graph import build_growth_coach_graph
    from app.domain.models.enums import CoachPersonality
    from app.infrastructure.database.models.goal import Goal
    from app.infrastructure.database.models.growth_dna import GrowthDNA
    from app.infrastructure.database.models.user import User
    from tests.conftest import TestingSessionLocal

    db = TestingSessionLocal()
    try:
        user = User(
            email="g@test.com",
            username="guser",
            hashed_password="x",
            coach_personality=CoachPersonality.TEACHER,
        )
        db.add(user)
        db.flush()
        db.add(GrowthDNA(user_id=user.id, growth_score=10.0))
        today = date.today()
        goal = Goal(
            user_id=user.id,
            title="Test Goal",
            priority=3,
            start_date=today,
            end_date=today + timedelta(days=30),
            target_date=today + timedelta(days=30),
        )
        db.add(goal)
        db.commit()

        graph = build_growth_coach_graph(db)
        result = graph.invoke(
            {
                "user_id": user.id,
                "goal_id": goal.id,
                "goal_title": goal.title,
                "goal_description": "",
                "start_date": today.isoformat(),
                "end_date": (today + timedelta(days=30)).isoformat(),
                "coach_personality": "teacher",
            }
        )
        assert result["current_step"] == "memory_save"
        assert len(result["daily_missions"]) >= 1
    finally:
        db.close()
