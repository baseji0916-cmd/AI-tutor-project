"""
SQLAlchemy engine and session factory (STEP 2).

Central database connection used by repositories and FastAPI dependencies.
"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config.settings import get_settings


class Base(DeclarativeBase):
    """SQLAlchemy 2.x declarative base for all ORM models."""


settings = get_settings()

connect_args = (
    {"check_same_thread": False}
    if settings.database_url.startswith("sqlite")
    else {}
)

engine = create_engine(
    settings.database_url,
    connect_args=connect_args,
    echo=settings.debug,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency — yields one DB session per request.

    Yields:
        Active SQLAlchemy Session (always closed after use).
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
