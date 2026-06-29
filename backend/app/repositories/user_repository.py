"""User repository (STEP 2/3)."""

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Data access for User entities."""

    model = User

    def get_by_email(self, email: str) -> User | None:
        """Find user by email address (case-insensitive)."""
        return self.db.query(User).filter(User.email == email.lower()).first()

    def get_by_username(self, username: str) -> User | None:
        """Find user by username (case-insensitive)."""
        return self.db.query(User).filter(User.username == username.lower()).first()

    def get_by_id(self, user_id: int) -> User | None:
        """Find user by primary key."""
        return self.db.get(User, user_id)
