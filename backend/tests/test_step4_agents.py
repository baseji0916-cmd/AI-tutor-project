"""STEP 4 AI Growth Agent integration tests."""

from fastapi.testclient import TestClient

from tests.conftest import create_user_and_goal


def test_ai_capabilities(client: TestClient) -> None:
    """GET /api/ai — list all agents."""
    resp = client.get("/api/ai")
    assert resp.status_code == 200
    agents = resp.json()["agents"]
    assert len(agents) >= 11
    ids = {a["id"] for a in agents}
    assert "goal_agent" in ids
    assert "auto_replanner" in ids
    assert "growth_predictor" in ids


def test_step4_goal_and_planner(client: TestClient) -> None:
    headers, goal_id = create_user_and_goal(client)

    analyze = client.post(f"/api/ai/goal/{goal_id}/analyze", headers=headers)
    assert analyze.status_code == 200
    assert 0 <= analyze.json()["realism_score"] <= 100
    assert len(analyze.json()["sub_goals"]) >= 2

    plan = client.post(f"/api/ai/planner/{goal_id}/generate", headers=headers)
    assert plan.status_code == 200
    assert len(plan.json()["plans"]) == 2
    assert len(plan.json()["missions"]) >= 1


def test_step4_growth_dna_and_predictor(client: TestClient) -> None:
    headers, goal_id = create_user_and_goal(client)

    dna = client.get("/api/ai/growth-dna", headers=headers)
    assert dna.status_code == 200
    assert "focus_time" in dna.json()

    predictor = client.post(f"/api/ai/predictor/{goal_id}", headers=headers)
    assert predictor.status_code == 200
    assert 0 <= predictor.json()["achievement_probability"] <= 100
    assert predictor.json()["confidence_level"] in {"high", "medium", "low"}


def test_step4_simulation_story_recommendations(client: TestClient) -> None:
    headers, goal_id = create_user_and_goal(client)

    sim = client.post(f"/api/ai/simulation/{goal_id}", headers=headers)
    assert sim.status_code == 200
    assert len(sim.json()["scenarios"]) == 3

    story = client.get("/api/ai/timeline/story", headers=headers)
    assert story.status_code == 200
    assert story.json()["story"]

    rec = client.get("/api/ai/recommendations", headers=headers)
    assert rec.status_code == 200
    assert len(rec.json()["books"]) >= 1

    timeline = client.get("/api/ai/timeline", headers=headers)
    assert timeline.status_code == 200


def test_step4_failure_replanner_personality(client: TestClient) -> None:
    headers, goal_id = create_user_and_goal(client)

    plan = client.post(f"/api/ai/planner/{goal_id}/generate", headers=headers)
    mission_id = plan.json()["missions"][0]["id"]

    client.post(f"/api/v1/missions/{mission_id}/fail", json={"notes": "시간 부족"}, headers=headers)

    failure = client.post(
        f"/api/ai/failure/{mission_id}/analyze?auto_replan=true",
        json={"notes": "시간 부족"},
        headers=headers,
    )
    assert failure.status_code == 200
    assert failure.json()["root_causes"]
    assert failure.json()["dna_updated"] is True
    assert failure.json()["replanned"] is True
    assert failure.json()["replan"]["plans"]

    replan = client.post(f"/api/ai/replanner/{goal_id}", headers=headers)
    assert replan.status_code == 200
    assert replan.json()["revision_summary"]

    personality = client.get("/api/ai/personality", headers=headers)
    assert personality.status_code == 200
    assert len(personality.json()["available"]) == 5

    updated = client.put(
        "/api/ai/personality",
        json={"personality": "ceo"},
        headers=headers,
    )
    assert updated.json()["current"] == "ceo"

    coach = client.post(
        "/api/ai/coach/feedback",
        json={"context": "목표 달성이 어려워요"},
        headers=headers,
    )
    assert coach.status_code == 200
    assert coach.json()["message"]
