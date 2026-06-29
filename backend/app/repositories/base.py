"""Generic repository base class (STEP 2)."""

from typing import Generic, TypeVar

from sqlalchemy.orm import Session

from app.database.connection import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    """
    Reusable CRUD operations for SQLAlchemy models.

    Subclasses set `model` to the ORM class they manage.
    """

    model: type[ModelT]

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, entity_id: int) -> ModelT | None:
        """Fetch a single record by primary key."""
        return self.db.get(self.model, entity_id)

    def list_all(self) -> list[ModelT]:
        """Return all records (use pagination in production)."""
        return self.db.query(self.model).all()

    def add(self, entity: ModelT) -> ModelT:
        """Persist a new entity."""
        self.db.add(entity)
        self.db.flush()
        return entity

    def delete(self, entity: ModelT) -> None:
        """Remove an entity from the session."""
        self.db.delete(entity)
        self.db.flush()

    def commit(self) -> None:
        """Commit the current transaction."""
        self.db.commit()

    def refresh(self, entity: ModelT) -> ModelT:
        """Reload entity state from the database."""
        self.db.refresh(entity)
        return entity
