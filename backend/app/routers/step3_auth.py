"""
STEP 3 인증 API.

엔드포인트:
  POST /auth/signup  — 회원가입
  POST /auth/login   — 로그인 (JWT 발급)
  GET  /auth/me      — 현재 로그인 사용자
"""

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.api.dependencies import get_current_user, get_step3_auth_service
from app.models.user import User
from app.schemas.auth import Token
from app.schemas.step3_auth import LoginRequest, SignupRequest, UserMeResponse
from app.services.step3_auth_service import Step3AuthService

router = APIRouter(prefix="/auth", tags=["Auth (STEP 3)"])


@router.post("/signup", response_model=UserMeResponse, status_code=201)
def signup(
    data: SignupRequest,
    auth_service: Step3AuthService = Depends(get_step3_auth_service),
) -> UserMeResponse:
    """회원가입 — 비밀번호는 bcrypt로 암호화되어 저장됩니다."""
    return auth_service.signup(data)


@router.post("/login", response_model=Token)
def login(
    data: LoginRequest,
    auth_service: Step3AuthService = Depends(get_step3_auth_service),
) -> Token:
    """로그인 — 성공 시 JWT access_token을 반환합니다."""
    return auth_service.login(data)


@router.post("/login/form", response_model=Token, include_in_schema=False)
def login_form(
    form: OAuth2PasswordRequestForm = Depends(),
    auth_service: Step3AuthService = Depends(get_step3_auth_service),
) -> Token:
    """Swagger UI 'Authorize' 버튼용 (username 필드에 이메일 입력)."""
    return auth_service.login(LoginRequest(email=form.username, password=form.password))


@router.get("/me", response_model=UserMeResponse)
def get_me(
    current_user: User = Depends(get_current_user),
    auth_service: Step3AuthService = Depends(get_step3_auth_service),
) -> UserMeResponse:
    """JWT로 인증된 현재 사용자 정보를 반환합니다."""
    return auth_service.get_me(current_user)
