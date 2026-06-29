"""
STEP 3 authentication service.

Service Layer: HTTP 라우터와 Repository 사이의 비즈니스 로직.
- 비밀번호 bcrypt 암호화
- JWT 토큰 발급
- 중복 이메일 검증
"""

import re

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.models.growth_dna import GrowthDNA
from app.models.user import User
from app.repositories.growth_dna_repository import GrowthDNARepository
from app.repositories.user_repository import UserRepository
from app.schemas.auth import Token
from app.schemas.step3_auth import LoginRequest, SignupRequest, UserMeResponse


class Step3AuthService:
    """회원가입, 로그인, 현재 사용자 조회."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.user_repo = UserRepository(db)
        self.dna_repo = GrowthDNARepository(db)

    def signup(self, data: SignupRequest) -> UserMeResponse:
        """
        회원가입 처리.

        1. 이메일 중복 확인
        2. 비밀번호 bcrypt 해시
        3. User + GrowthDNA 저장
        """
        email = data.email.lower()
        if self.user_repo.get_by_email(email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )

        # username은 이메일 @ 앞부분으로 자동 생성 (고유성 보장)
        base_username = re.sub(r"[^a-z0-9_]", "", email.split("@")[0].lower()) or "user"
        username = base_username
        suffix = 1
        while self.user_repo.get_by_username(username):
            username = f"{base_username}{suffix}"
            suffix += 1

        user = User(
            name=data.name.strip(),
            email=email,
            username=username,
            password_hash=hash_password(data.password),
            occupation=data.occupation,
            health_info=data.health_info,
        )
        self.user_repo.add(user)
        self.dna_repo.add(GrowthDNA(user_id=user.id, growth_score=0.0))
        self.user_repo.commit()
        self.user_repo.refresh(user)
        return UserMeResponse.model_validate(user)

    def login(self, data: LoginRequest) -> Token:
        """
        로그인 처리.

        이메일/비밀번호 검증 후 JWT access_token 반환.
        """
        user = self.user_repo.get_by_email(data.email.lower())
        if not user or not verify_password(data.password, user.password_hash):
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

    def get_me(self, user: User) -> UserMeResponse:
        """현재 로그인 사용자 프로필 반환."""
        return UserMeResponse.model_validate(user)
