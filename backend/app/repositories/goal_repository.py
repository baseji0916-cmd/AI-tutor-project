"""Goal repository (STEP 2/3)."""

from app.models.goal import Goal
from app.repositories.base import BaseRepository


class GoalRepository(BaseRepository[Goal]):
    """Data access for Goal entities."""

    model = Goal

    def list_by_user(self, user_id: int) -> list[Goal]:
        """Return all goals belonging to a user, ordered by priority then target date."""
        return (
            self.db.query(Goal)
            .filter(Goal.user_id == user_id)
            .order_by(Goal.priority.asc(), Goal.target_date.asc())
            .all()
        )

    def get_by_id_and_user(self, goal_id: int, user_id: int) -> Goal | None:
        """Fetch one goal only if it belongs to the given user."""
        return (
            self.db.query(Goal)
            .filter(Goal.id == goal_id, Goal.user_id == user_id)
            .first()
        )
