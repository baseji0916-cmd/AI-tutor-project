"""Initial schema — users, goals, plans, missions, growth_dna, logs, timeline.

Revision ID: 001
Create Date: 2026-06-29
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("username", sa.String(length=50), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=100), nullable=True),
        sa.Column("bio", sa.Text(), nullable=True),
        sa.Column(
            "coach_personality",
            sa.Enum(
                "teacher", "friend", "passion", "data_analyst", "ceo", "tsundere",
                name="coachpersonality",
            ),
            nullable=False,
        ),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=True)

    op.create_table(
        "goals",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("priority", sa.Integer(), nullable=False),
        sa.Column(
            "status",
            sa.Enum("active", "completed", "paused", "abandoned", name="goalstatus"),
            nullable=False,
        ),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_goals_id"), "goals", ["id"], unique=False)
    op.create_index(op.f("ix_goals_user_id"), "goals", ["user_id"], unique=False)

    op.create_table(
        "growth_dna",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("focus_time_minutes", sa.Integer(), nullable=False),
        sa.Column("failure_patterns", sa.Text(), nullable=True),
        sa.Column("success_patterns", sa.Text(), nullable=True),
        sa.Column("execution_style", sa.Text(), nullable=True),
        sa.Column("preferred_feedback", sa.Text(), nullable=True),
        sa.Column("growth_score", sa.Float(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_growth_dna_id"), "growth_dna", ["id"], unique=False)
    op.create_index(op.f("ix_growth_dna_user_id"), "growth_dna", ["user_id"], unique=True)

    op.create_table(
        "timeline_events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column(
            "event_type",
            sa.Enum(
                "goal_created", "goal_completed", "mission_completed",
                "mission_failed", "milestone", "reflection", "score_update",
                name="timelineeventtype",
            ),
            nullable=False,
        ),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("metadata_json", sa.Text(), nullable=True),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_timeline_events_id"), "timeline_events", ["id"], unique=False)
    op.create_index(op.f("ix_timeline_events_occurred_at"), "timeline_events", ["occurred_at"], unique=False)
    op.create_index(op.f("ix_timeline_events_user_id"), "timeline_events", ["user_id"], unique=False)

    op.create_table(
        "plans",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("goal_id", sa.Integer(), nullable=False),
        sa.Column(
            "plan_type",
            sa.Enum("monthly", "weekly", "daily", name="plantype"),
            nullable=False,
        ),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["goal_id"], ["goals.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_plans_goal_id"), "plans", ["goal_id"], unique=False)
    op.create_index(op.f("ix_plans_id"), "plans", ["id"], unique=False)
    op.create_index(op.f("ix_plans_user_id"), "plans", ["user_id"], unique=False)

    op.create_table(
        "missions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("goal_id", sa.Integer(), nullable=False),
        sa.Column("plan_id", sa.Integer(), nullable=True),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("scheduled_date", sa.Date(), nullable=False),
        sa.Column(
            "status",
            sa.Enum("pending", "completed", "failed", "skipped", name="missionstatus"),
            nullable=False,
        ),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["goal_id"], ["goals.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["plan_id"], ["plans.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_missions_goal_id"), "missions", ["goal_id"], unique=False)
    op.create_index(op.f("ix_missions_id"), "missions", ["id"], unique=False)
    op.create_index(op.f("ix_missions_plan_id"), "missions", ["plan_id"], unique=False)
    op.create_index(op.f("ix_missions_scheduled_date"), "missions", ["scheduled_date"], unique=False)
    op.create_index(op.f("ix_missions_user_id"), "missions", ["user_id"], unique=False)

    op.create_table(
        "execution_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("goal_id", sa.Integer(), nullable=True),
        sa.Column("mission_id", sa.Integer(), nullable=True),
        sa.Column("action_type", sa.String(length=50), nullable=False),
        sa.Column(
            "status",
            sa.Enum("success", "failure", name="executionstatus"),
            nullable=False,
        ),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("duration_minutes", sa.Integer(), nullable=True),
        sa.Column("logged_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["goal_id"], ["goals.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["mission_id"], ["missions.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_execution_logs_goal_id"), "execution_logs", ["goal_id"], unique=False)
    op.create_index(op.f("ix_execution_logs_id"), "execution_logs", ["id"], unique=False)
    op.create_index(op.f("ix_execution_logs_mission_id"), "execution_logs", ["mission_id"], unique=False)
    op.create_index(op.f("ix_execution_logs_user_id"), "execution_logs", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_table("execution_logs")
    op.drop_table("missions")
    op.drop_table("plans")
    op.drop_table("timeline_events")
    op.drop_table("growth_dna")
    op.drop_table("goals")
    op.drop_table("users")
    op.execute("DROP TYPE IF EXISTS executionstatus")
    op.execute("DROP TYPE IF EXISTS missionstatus")
    op.execute("DROP TYPE IF EXISTS plantype")
    op.execute("DROP TYPE IF EXISTS timelineeventtype")
    op.execute("DROP TYPE IF EXISTS goalstatus")
    op.execute("DROP TYPE IF EXISTS coachpersonality")
