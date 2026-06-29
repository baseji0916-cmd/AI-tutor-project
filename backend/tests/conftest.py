"""Shared pytest fixtures for GrowthPilot backend tests."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.config.settings import get_settings
from app.infrastructure.database.models import (  # noqa: F401
    ExecutionLog,
    Goal,
    GrowthDNA,
    Mission,
    Plan,
    TimelineEvent,
    User,
)
from app.main import app

TEST_DATABASE_URL = "sqlite://"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def force_mock_llm(monkeypatch: pytest.MonkeyPatch) -> None:
    """Agent tests expect mock mode — clear OpenAI key so no live API calls."""
    monkeypatch.setenv("OPENAI_API_KEY", "")
    get_settings.cache_clear()


@pytest.fixture(autouse=True)
def setup_database() -> None:
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client() -> TestClient:
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def db_session() -> Session:
    """Direct DB session for database unit tests."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_user_and_goal(client: TestClient) -> tuple[dict[str, str], int]:
    """Register user, login, create goal — returns auth headers and goal_id."""
    from datetime import date, timedelta

    client.post(
        "/api/v1/auth/register",
        json={
            "email": "shared@test.com",
            "username": "shareduser",
            "password": "securepass123",
        },
    )
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "shared@test.com", "password": "securepass123"},
    )
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    today = date.today()
    goal_resp = client.post(
        "/api/v1/goals",
        json={
            "title": "Python 마스터",
            "description": "FastAPI와 LangGraph 학습",
            "priority": 1,
            "start_date": today.isoformat(),
            "end_date": (today + timedelta(days=60)).isoformat(),
        },
        headers=headers,
    )
    return headers, goal_resp.json()["id"]
