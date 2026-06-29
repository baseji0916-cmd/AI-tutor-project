"""
Authentication application service (legacy /api/v1).

Repository Pattern 적용 — DB 접근은 UserRepository에 위임.
"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.models.growth_dna import GrowthDNA
from app.models.user import User
from app.repositories.growth_dna_repository import GrowthDNARepository
from app.repositories.user_repository import UserRepository
from app.schemas.auth import Token
from app.schemas.user import UserCreate, UserLogin, UserResponse, UserUpdate


class AuthService:
    """Handles registration, login, and profile operations."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.user_repo = UserRepository(db)
        self.dna_repo = GrowthDNARepository(db)

    def register(self, data: UserCreate) -> UserResponse:
        """Create a new user account."""
        if self.user_repo.get_by_email(data.email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )
        if self.user_repo.get_by_username(data.username):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already taken",
            )

        user = User(
            name=(data.full_name or data.username).strip(),
            email=data.email.lower(),
            username=data.username.lower(),
            hashed_password=hash_password(data.password),
            full_name=data.full_name,
            coach_personality=data.coach_personality,
        )
        self.user_repo.add(user)
        self.dna_repo.add(GrowthDNA(user_id=user.id, growth_score=0.0))
        self.user_repo.commit()
        self.user_repo.refresh(user)
        return UserResponse.model_validate(user)

    def login(self, data: UserLogin) -> Token:
        """Authenticate user and return JWT access token."""
        user = self.user_repo.get_by_email(data.email.lower())
        if not user or not verify_password(data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is deactivated",
            )

        token = create_access_token(subject=str(user.id))
        return Token(access_token=token)

    def get_user_by_id(self, user_id: int) -> User | None:
        """Fetch user by primary key."""
        return self.user_repo.get_by_id(user_id)

    def update_profile(self, user: User, data: UserUpdate) -> UserResponse:
        """Update authenticated user's profile fields."""
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)

        self.user_repo.commit()
        self.user_repo.refresh(user)
        return UserResponse.model_validate(user)
