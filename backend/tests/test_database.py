"""STEP 2 database connection and model tests."""

from datetime import date, timedelta

import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.database.connection import engine
from app.domain.models.enums import CoachPersonality, GoalStatus
from app.models.enums import TaskType
from app.models.feedback import Feedback
from app.models.goal import Goal
from app.models.growth_dna import GrowthDNA
from app.models.recommendation import Recommendation
from app.models.task import Task
from app.models.user import User
from app.repositories.goal_repository import GoalRepository
from app.repositories.user_repository import UserRepository


def test_database_connection() -> None:
    """Verify SQLite engine accepts a simple query."""
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1")).scalar()
    assert result == 1


def test_user_goal_relationship(db_session: Session) -> None:
    """User → Goal (1:N) relationship works."""
    user = User(
        name="Test User",
        email="dbtest@example.com",
        username="dbtest",
        password_hash=hash_password("pass1234"),
        coach_personality=CoachPersonality.FRIEND,
    )
    db_session.add(user)
    db_session.flush()

    today = date.today()
    goal = Goal(
        user_id=user.id,
        title="Learn FastAPI",
        target_date=today + timedelta(days=30),
        start_date=today,
        end_date=today + timedelta(days=30),
        priority=1,
        status=GoalStatus.ACTIVE,
        progress=0.0,
    )
    db_session.add(goal)
    db_session.commit()

    db_session.refresh(user)
    assert len(user.goals) == 1
    assert user.goals[0].title == "Learn FastAPI"


def test_goal_task_relationship(db_session: Session) -> None:
    """Goal → Task (1:N) relationship works."""
    user = User(
        name="Task User",
        email="task@example.com",
        username="taskuser",
        password_hash=hash_password("pass1234"),
        coach_personality=CoachPersonality.TEACHER,
    )
    goal = Goal(
        user=user,
        title="Daily Study",
        target_date=date.today() + timedelta(days=7),
        start_date=date.today(),
        end_date=date.today() + timedelta(days=7),
        priority=2,
    )
    task = Task(
        goal=goal,
        title="Read docs",
        due_date=date.today(),
        task_type=TaskType.DAILY,
        completed=False,
    )
    db_session.add_all([user, goal, task])
    db_session.commit()

    db_session.refresh(goal)
    assert len(goal.tasks) == 1
    assert goal.tasks[0].task_type == TaskType.DAILY


def test_user_growth_dna_one_to_one(db_session: Session) -> None:
    """User → GrowthDNA (1:1) relationship works."""
    user = User(
        name="DNA User",
        email="dna@example.com",
        username="dnauser",
        password_hash=hash_password("pass1234"),
        coach_personality=CoachPersonality.DATA_ANALYST,
    )
    dna = GrowthDNA(user=user, focus_time=45, growth_score=10.0)
    db_session.add_all([user, dna])
    db_session.commit()

    db_session.refresh(user)
    assert user.growth_dna is not None
    assert user.growth_dna.focus_time == 45


def test_goal_feedback_and_user_recommendation(db_session: Session) -> None:
    """Goal → Feedback (1:N) and User → Recommendation (1:N)."""
    user = User(
        name="Feedback User",
        email="fb@example.com",
        username="fbuser",
        password_hash=hash_password("pass1234"),
        coach_personality=CoachPersonality.CEO,
    )
    goal = Goal(
        user=user,
        title="Run 5K",
        target_date=date.today() + timedelta(days=14),
        start_date=date.today(),
        end_date=date.today() + timedelta(days=14),
        priority=1,
    )
    feedback = Feedback(goal=goal, feedback_type="coach", content="Great pace today!")
    recommendation = Recommendation(
        user=user,
        category="health",
        title="Stretch routine",
        description="Add 10 min stretching after runs.",
    )
    db_session.add_all([user, goal, feedback, recommendation])
    db_session.commit()

    db_session.refresh(goal)
    db_session.refresh(user)
    assert len(goal.feedbacks) == 1
    assert len(user.recommendations) == 1


def test_user_repository_get_by_email(db_session: Session) -> None:
    """UserRepository finds users by email."""
    user = User(
        name="Repo User",
        email="repo@example.com",
        username="repouser",
        password_hash=hash_password("pass1234"),
        coach_personality=CoachPersonality.TEACHER,
    )
    db_session.add(user)
    db_session.commit()

    repo = UserRepository(db_session)
    found = repo.get_by_email("repo@example.com")
    assert found is not None
    assert found.name == "Repo User"


def test_goal_repository_list_by_user(db_session: Session) -> None:
    """GoalRepository lists goals for a user."""
    user = User(
        name="Goal Repo",
        email="goalrepo@example.com",
        username="goalrepo",
        password_hash=hash_password("pass1234"),
        coach_personality=CoachPersonality.FRIEND,
    )
    db_session.add(user)
    db_session.flush()

    today = date.today()
    db_session.add_all(
        [
            Goal(
                user_id=user.id,
                title="A",
                target_date=today,
                start_date=today,
                end_date=today,
                priority=1,
            ),
            Goal(
                user_id=user.id,
                title="B",
                target_date=today,
                start_date=today,
                end_date=today,
                priority=2,
            ),
        ]
    )
    db_session.commit()

    repo = GoalRepository(db_session)
    goals = repo.list_by_user(user.id)
    assert len(goals) == 2
    assert goals[0].title == "A"
