"""Mission and extended agent API tests."""

from fastapi.testclient import TestClient

from tests.conftest import create_user_and_goal


def test_mission_complete_flow(client: TestClient) -> None:
    headers, goal_id = create_user_and_goal(client)
    plan_resp = client.post(f"/api/v1/agents/goals/{goal_id}/generate-plan", headers=headers)
    assert plan_resp.status_code == 200
    mission_id = plan_resp.json()["missions"][0]["id"]

    today = client.get("/api/v1/missions/today", headers=headers)
    assert today.status_code == 200

    complete = client.post(f"/api/v1/missions/{mission_id}/complete", headers=headers)
    assert complete.status_code == 200
    assert complete.json()["status"] == "completed"


def test_coach_and_recommendations(client: TestClient) -> None:
    headers, _ = create_user_and_goal(client)
    rec = client.get("/api/v1/agents/recommendations", headers=headers)
    assert rec.status_code == 200
    assert len(rec.json()["books"]) >= 1

    coach = client.post(
        "/api/v1/agents/coach/feedback",
        json={"context": "오늘 미션이 어려워요"},
        headers=headers,
    )
    assert coach.status_code == 200
    assert coach.json()["message"]


def test_future_simulation_and_story(client: TestClient) -> None:
    headers, goal_id = create_user_and_goal(client)
    sim = client.post(f"/api/v1/agents/goals/{goal_id}/simulate", headers=headers)
    assert sim.status_code == 200
    assert len(sim.json()["scenarios"]) == 3

    story = client.get("/api/v1/agents/timeline/story", headers=headers)
    assert story.status_code == 200
    assert story.json()["story"]


def test_failure_analysis(client: TestClient) -> None:
    headers, goal_id = create_user_and_goal(client)
    plan = client.post(f"/api/v1/agents/goals/{goal_id}/generate-plan", headers=headers)
    mission_id = plan.json()["missions"][0]["id"]

    client.post(f"/api/v1/missions/{mission_id}/fail", json={"notes": "시간 부족"}, headers=headers)
    analysis = client.post(
        f"/api/v1/agents/missions/{mission_id}/analyze-failure",
        json={"notes": "시간 부족"},
        headers=headers,
    )
    assert analysis.status_code == 200
    assert analysis.json()["root_causes"]
