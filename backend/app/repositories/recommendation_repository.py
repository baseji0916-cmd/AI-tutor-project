"""Recommendation repository (STEP 2)."""

from app.models.recommendation import Recommendation
from app.repositories.base import BaseRepository


class RecommendationRepository(BaseRepository[Recommendation]):
    """Data access for Recommendation entities."""

    model = Recommendation

    def list_by_user(self, user_id: int) -> list[Recommendation]:
        """Return recommendations for a user."""
        return self.db.query(Recommendation).filter(Recommendation.user_id == user_id).all()
