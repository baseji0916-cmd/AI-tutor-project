"""GrowthDNA repository (STEP 2)."""

from app.models.growth_dna import GrowthDNA
from app.repositories.base import BaseRepository


class GrowthDNARepository(BaseRepository[GrowthDNA]):
    """Data access for GrowthDNA profiles."""

    model = GrowthDNA

    def get_by_user_id(self, user_id: int) -> GrowthDNA | None:
        """Fetch GrowthDNA profile for a user (1:1)."""
        return self.db.query(GrowthDNA).filter(GrowthDNA.user_id == user_id).first()
