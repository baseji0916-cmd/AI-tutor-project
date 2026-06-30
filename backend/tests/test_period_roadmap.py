"""Tests for period roadmap API."""

from fastapi.testclient import TestClient

from tests.conftest import create_user_and_goal


def test_period_roadmap_returns_all_horizons(client: TestClient) -> None:
    headers, _goal_id = create_user_and_goal(client)

    resp = client.get("/api/v1/dashboard/period-roadmap", headers=headers)
    assert resp.status_code == 200
    data = resp.json()

    assert "daily" in data
    assert "weekly" in data
    assert "monthly" in data
    assert data["daily"]["horizon"] == "daily"
    assert data["weekly"]["horizon"] == "weekly"
    assert data["monthly"]["horizon"] == "monthly"
    assert len(data["daily"]["items"]) >= 1
    assert len(data["weekly"]["items"]) >= 1
    assert len(data["monthly"]["items"]) >= 1
    assert len(data["overall_goals"]) >= 1


def test_period_roadmap_includes_missions_after_plan(client: TestClient) -> None:
    headers, goal_id = create_user_and_goal(client)

    plan = client.post(f"/api/v1/agents/goals/{goal_id}/generate-plan", headers=headers)
    assert plan.status_code == 200

    resp = client.get("/api/v1/dashboard/period-roadmap", headers=headers)
    data = resp.json()

    mission_items = [i for i in data["daily"]["items"] if i["source"] == "mission"]
    assert len(mission_items) >= 1
    assert data["daily"]["is_template"] is False
