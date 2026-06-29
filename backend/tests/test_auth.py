"""Authentication API tests."""

from fastapi.testclient import TestClient


def test_root(client: TestClient) -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert "GrowthPilot" in response.json()["message"]


def test_health(client: TestClient) -> None:
    response = client.get("/api/v1/health")
    assert response.json()["status"] == "healthy"


def test_register_and_login(client: TestClient) -> None:
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "coach@test.com",
            "username": "testuser",
            "password": "securepass123",
            "full_name": "Test User",
            "coach_personality": "teacher",
        },
    )
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "coach@test.com", "password": "securepass123"},
    )
    token = login.json()["access_token"]
    me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.json()["full_name"] == "Test User"


def test_register_duplicate_email(client: TestClient) -> None:
    payload = {
        "email": "dup@test.com",
        "username": "userone",
        "password": "securepass123",
    }
    client.post("/api/v1/auth/register", json=payload)
    payload["username"] = "usertwo"
    assert client.post("/api/v1/auth/register", json=payload).status_code == 409
