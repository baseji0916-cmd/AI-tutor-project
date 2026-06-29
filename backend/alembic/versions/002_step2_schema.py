"""STEP 2 schema - tasks, feedbacks, recommendations + new columns.

Revision ID: 002
Revises: 001
Create Date: 2026-06-29
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- users: STEP 2 profile fields ---
    with op.batch_alter_table("users") as batch_op:
        batch_op.add_column(sa.Column("name", sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column("occupation", sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column("health_info", sa.Text(), nullable=True))

    op.execute("UPDATE users SET name = COALESCE(full_name, username, email) WHERE name IS NULL")
    with op.batch_alter_table("users") as batch_op:
        batch_op.alter_column("name", nullable=False)

    # --- goals: target_date + progress ---
    with op.batch_alter_table("goals") as batch_op:
        batch_op.add_column(sa.Column("target_date", sa.Date(), nullable=True))
        batch_op.add_column(sa.Column("progress", sa.Float(), server_default="0", nullable=False))

    op.execute("UPDATE goals SET target_date = end_date WHERE target_date IS NULL")
    with op.batch_alter_table("goals") as batch_op:
        batch_op.alter_column("target_date", nullable=False)

    # --- tasks (STEP 2) ---
    op.create_table(
        "tasks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("goal_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("due_date", sa.Date(), nullable=False),
        sa.Column(
            "task_type",
            sa.Enum("daily", "weekly", "monthly", name="tasktype"),
            nullable=False,
        ),
        sa.Column("completed", sa.Boolean(), server_default="0", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["goal_id"], ["goals.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_tasks_id"), "tasks", ["id"], unique=False)
    op.create_index(op.f("ix_tasks_goal_id"), "tasks", ["goal_id"], unique=False)

    # --- feedbacks (STEP 2) ---
    op.create_table(
        "feedbacks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("goal_id", sa.Integer(), nullable=False),
        sa.Column("feedback_type", sa.String(length=50), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["goal_id"], ["goals.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_feedbacks_id"), "feedbacks", ["id"], unique=False)
    op.create_index(op.f("ix_feedbacks_goal_id"), "feedbacks", ["goal_id"], unique=False)

    # --- recommendations (STEP 2) ---
    op.create_table(
        "recommendations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("category", sa.String(length=50), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_recommendations_id"), "recommendations", ["id"], unique=False)
    op.create_index(op.f("ix_recommendations_user_id"), "recommendations", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_recommendations_user_id"), table_name="recommendations")
    op.drop_index(op.f("ix_recommendations_id"), table_name="recommendations")
    op.drop_table("recommendations")

    op.drop_index(op.f("ix_feedbacks_goal_id"), table_name="feedbacks")
    op.drop_index(op.f("ix_feedbacks_id"), table_name="feedbacks")
    op.drop_table("feedbacks")

    op.drop_index(op.f("ix_tasks_goal_id"), table_name="tasks")
    op.drop_index(op.f("ix_tasks_id"), table_name="tasks")
    op.drop_table("tasks")

    with op.batch_alter_table("goals") as batch_op:
        batch_op.drop_column("progress")
        batch_op.drop_column("target_date")

    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_column("health_info")
        batch_op.drop_column("occupation")
        batch_op.drop_column("name")

    op.execute("DROP TYPE IF EXISTS tasktype")
