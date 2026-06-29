"""STEP 3 authentication and goal management tests."""

from datetime import date, timedelta

from fastapi.testclient import TestClient


def _signup_and_login(client: TestClient, email: str = "step3@test.com") -> dict[str, str]:
    """Helper: 회원가입 후 Bearer 헤더 반환."""
    client.post(
        "/auth/signup",
        json={
            "name": "Step3 User",
            "email": email,
            "password": "securepass123",
            "occupation": "Developer",
        },
    )
    login = client.post(
        "/auth/login",
        json={"email": email, "password": "securepass123"},
    )
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_signup_login_me(client: TestClient) -> None:
    """POST /auth/signup → POST /auth/login → GET /auth/me"""
    headers = _signup_and_login(client)
    me = client.get("/auth/me", headers=headers)
    assert me.status_code == 200
    data = me.json()
    assert data["name"] == "Step3 User"
    assert data["email"] == "step3@test.com"
    assert data["occupation"] == "Developer"


def test_signup_duplicate_email(client: TestClient) -> None:
    client.post(
        "/auth/signup",
        json={"name": "A", "email": "dup2@test.com", "password": "securepass123"},
    )
    resp = client.post(
        "/auth/signup",
        json={"name": "B", "email": "dup2@test.com", "password": "securepass123"},
    )
    assert resp.status_code == 409


def test_login_invalid_password(client: TestClient) -> None:
    client.post(
        "/auth/signup",
        json={"name": "X", "email": "badlogin@test.com", "password": "securepass123"},
    )
    resp = client.post(
        "/auth/login",
        json={"email": "badlogin@test.com", "password": "wrongpassword"},
    )
    assert resp.status_code == 401


def test_goal_crud(client: TestClient) -> None:
    """POST/GET/PUT/DELETE /goal 전체 CRUD"""
    headers = _signup_and_login(client, email="goalstep3@test.com")
    today = date.today()
    end = today + timedelta(days=60)

    create = client.post(
        "/goal",
        json={
            "title": "Python 마스터",
            "description": "FastAPI 학습",
            "target_period": {
                "start_date": today.isoformat(),
                "end_date": end.isoformat(),
            },
            "priority": 1,
            "progress": 0.0,
        },
        headers=headers,
    )
    assert create.status_code == 201
    goal_id = create.json()["id"]
    assert create.json()["progress"] == 0.0
    assert create.json()["target_period"]["end_date"] == end.isoformat()

    listing = client.get("/goal", headers=headers)
    assert len(listing.json()) == 1

    detail = client.get(f"/goal/{goal_id}", headers=headers)
    assert detail.json()["title"] == "Python 마스터"

    updated = client.put(
        f"/goal/{goal_id}",
        json={
            "title": "Python Expert",
            "description": "Updated",
            "target_period": {
                "start_date": today.isoformat(),
                "end_date": end.isoformat(),
            },
            "priority": 2,
            "progress": 45.5,
            "status": "active",
        },
        headers=headers,
    )
    assert updated.status_code == 200
    assert updated.json()["progress"] == 45.5
    assert updated.json()["title"] == "Python Expert"

    delete = client.delete(f"/goal/{goal_id}", headers=headers)
    assert delete.status_code == 204
    assert client.get(f"/goal/{goal_id}", headers=headers).status_code == 404


def test_goal_requires_auth(client: TestClient) -> None:
    assert client.get("/goal").status_code == 401


def test_invalid_target_period(client: TestClient) -> None:
    headers = _signup_and_login(client, email="badperiod@test.com")
    today = date.today()
    resp = client.post(
        "/goal",
        json={
            "title": "Bad dates",
            "target_period": {
                "start_date": today.isoformat(),
                "end_date": (today - timedelta(days=1)).isoformat(),
            },
            "priority": 3,
        },
        headers=headers,
    )
    assert resp.status_code == 422
