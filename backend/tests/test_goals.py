"""Goal API tests."""

from datetime import date, timedelta

from fastapi.testclient import TestClient


def _auth_headers(client: TestClient) -> dict[str, str]:
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "goaluser@test.com",
            "username": "goaluser",
            "password": "securepass123",
        },
    )
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "goaluser@test.com", "password": "securepass123"},
    )
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


def test_create_and_list_goals(client: TestClient) -> None:
    headers = _auth_headers(client)
    today = date.today()
    payload = {
        "title": "영어 회화 마스터",
        "description": "매일 30분 스피킹 연습",
        "priority": 1,
        "start_date": today.isoformat(),
        "end_date": (today + timedelta(days=90)).isoformat(),
    }
    create_resp = client.post("/api/v1/goals", json=payload, headers=headers)
    assert create_resp.status_code == 201
    assert create_resp.json()["progress_rate"] == 0.0

    list_resp = client.get("/api/v1/goals", headers=headers)
    assert len(list_resp.json()) == 1


def test_update_and_delete_goal(client: TestClient) -> None:
    headers = _auth_headers(client)
    today = date.today()
    create_resp = client.post(
        "/api/v1/goals",
        json={
            "title": "운동 습관",
            "priority": 2,
            "start_date": today.isoformat(),
            "end_date": (today + timedelta(days=30)).isoformat(),
        },
        headers=headers,
    )
    goal_id = create_resp.json()["id"]
    patch_resp = client.patch(
        f"/api/v1/goals/{goal_id}",
        json={"status": "completed"},
        headers=headers,
    )
    assert patch_resp.json()["status"] == "completed"
    client.delete(f"/api/v1/goals/{goal_id}", headers=headers)
    assert client.get(f"/api/v1/goals/{goal_id}", headers=headers).status_code == 404


def test_dashboard_stats(client: TestClient) -> None:
    headers = _auth_headers(client)
    stats = client.get("/api/v1/dashboard/stats", headers=headers).json()
    assert stats["growth_score"] == 0.0


def test_invalid_date_range(client: TestClient) -> None:
    headers = _auth_headers(client)
    today = date.today()
    resp = client.post(
        "/api/v1/goals",
        json={
            "title": "잘못된 날짜",
            "priority": 3,
            "start_date": today.isoformat(),
            "end_date": (today - timedelta(days=1)).isoformat(),
        },
        headers=headers,
    )
    assert resp.status_code == 422
