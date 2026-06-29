"""Feedback repository (STEP 2)."""

from app.models.feedback import Feedback
from app.repositories.base import BaseRepository


class FeedbackRepository(BaseRepository[Feedback]):
    """Data access for Feedback entities."""

    model = Feedback

    def list_by_goal(self, goal_id: int) -> list[Feedback]:
        """Return feedback entries for a goal."""
        return self.db.query(Feedback).filter(Feedback.goal_id == goal_id).all()
