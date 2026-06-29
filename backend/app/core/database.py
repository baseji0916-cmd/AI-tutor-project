"""
Backward-compatible database module.

Delegates to app.database (STEP 2 canonical location).
"""

from app.database.connection import Base, SessionLocal, engine, get_db
from app.database.initializer import init_db

__all__ = ["Base", "SessionLocal", "engine", "get_db", "init_db"]
