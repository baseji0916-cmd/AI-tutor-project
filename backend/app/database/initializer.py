"""
Database initialization utilities (STEP 2).

Creates all tables registered on Base.metadata.
Patches older SQLite files when columns were added after first create_all().
"""

import app.models  # noqa: F401 — register ORM models
from sqlalchemy import inspect, text

from app.database.connection import Base, engine


def sync_schema() -> None:
    """Add columns missing from databases created before STEP 2 migrations."""
    inspector = inspect(engine)
    table_names = set(inspector.get_table_names())

    if "goals" in table_names:
        goal_cols = {c["name"] for c in inspector.get_columns("goals")}
        with engine.begin() as conn:
            if "target_date" not in goal_cols:
                conn.execute(text("ALTER TABLE goals ADD COLUMN target_date DATE"))
                conn.execute(
                    text("UPDATE goals SET target_date = end_date WHERE target_date IS NULL")
                )
            if "progress" not in goal_cols:
                conn.execute(
                    text("ALTER TABLE goals ADD COLUMN progress REAL NOT NULL DEFAULT 0")
                )

    if "users" in table_names:
        user_cols = {c["name"] for c in inspector.get_columns("users")}
        with engine.begin() as conn:
            if "name" not in user_cols:
                conn.execute(text("ALTER TABLE users ADD COLUMN name VARCHAR(100)"))
                conn.execute(
                    text(
                        "UPDATE users SET name = COALESCE(full_name, username, email) "
                        "WHERE name IS NULL"
                    )
                )
            if "occupation" not in user_cols:
                conn.execute(text("ALTER TABLE users ADD COLUMN occupation VARCHAR(100)"))
            if "health_info" not in user_cols:
                conn.execute(text("ALTER TABLE users ADD COLUMN health_info TEXT"))


def init_db() -> None:
    """Create all database tables if they do not exist, then patch legacy schema."""
    Base.metadata.create_all(bind=engine)
    sync_schema()


def drop_all_tables() -> None:
    """Drop every table — for tests only."""
    Base.metadata.drop_all(bind=engine)


def reset_db() -> None:
    """Drop and recreate all tables — for local dev reset."""
    drop_all_tables()
    init_db()
