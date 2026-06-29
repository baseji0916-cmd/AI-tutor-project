"""Task repository (STEP 2)."""

from app.models.task import Task
from app.repositories.base import BaseRepository


class TaskRepository(BaseRepository[Task]):
    """Data access for Task entities."""

    model = Task

    def list_by_goal(self, goal_id: int) -> list[Task]:
        """Return all tasks for a goal."""
        return self.db.query(Task).filter(Task.goal_id == goal_id).all()
