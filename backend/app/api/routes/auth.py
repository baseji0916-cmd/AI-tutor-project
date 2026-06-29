"""Authentication and profile API routes."""

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.api.dependencies import get_auth_service, get_current_user
from app.infrastructure.database.models.user import User
from app.schemas.auth import Token
from app.schemas.user import UserCreate, UserLogin, UserResponse, UserUpdate
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserResponse, status_code=201)
def register(
    data: UserCreate,
    auth_service: AuthService = Depends(get_auth_service),
) -> UserResponse:
    """Register a new user account."""
    return auth_service.register(data)


@router.post("/login", response_model=Token)
def login_json(
    data: UserLogin,
    auth_service: AuthService = Depends(get_auth_service),
) -> Token:
    """
    Login with JSON body (email + password).

    Preferred for frontend/mobile clients.
    """
    return auth_service.login(data)


@router.post("/login/form", response_model=Token)
def login_form(
    form: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service),
) -> Token:
    """
    OAuth2 password flow for Swagger UI 'Authorize' button.

    Uses `username` field for email address.
    """
    return auth_service.login(UserLogin(email=form.username, password=form.password))


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)) -> UserResponse:
    """Return the currently authenticated user's profile."""
    return UserResponse.model_validate(current_user)


@router.patch("/me", response_model=UserResponse)
def update_me(
    data: UserUpdate,
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
) -> UserResponse:
    """Update profile fields for the authenticated user."""
    return auth_service.update_profile(current_user, data)
