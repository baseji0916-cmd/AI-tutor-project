"""STEP 3 authentication request/response schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class SignupRequest(BaseModel):
    """
    회원가입 요청 body.

    - name: 표시 이름
    - email: 로그인에 사용할 이메일
    - password: 8자 이상 평문 비밀번호 (서버에서 bcrypt로 암호화)
    """

    name: str = Field(..., min_length=1, max_length=100, description="사용자 이름")
    email: EmailStr = Field(..., description="이메일 주소")
    password: str = Field(..., min_length=8, max_length=128, description="비밀번호")
    occupation: str | None = Field(None, max_length=100, description="직업 (선택)")
    health_info: str | None = Field(None, max_length=500, description="건강 정보 (선택)")


class LoginRequest(BaseModel):
    """로그인 요청 body — 이메일 + 비밀번호."""

    email: EmailStr
    password: str = Field(..., min_length=1)


class UserMeResponse(BaseModel):
    """GET /auth/me 응답 — 비밀번호 해시는 절대 포함하지 않습니다."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr
    occupation: str | None = None
    health_info: str | None = None
    created_at: datetime
    updated_at: datetime
