"""
FastAPI dependency injection.

Central place for auth guards and shared dependencies.
Routes import from here instead of duplicating JWT logic.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import User
from app.schemas.auth import TokenPayload
from app.services.auth_service import AuthService
from app.services.step3_auth_service import Step3AuthService
from app.services.step3_goal_service import Step3GoalService

# Swagger UI 'Authorize' — form login endpoint
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login/form")


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    """Provide AuthService with an injected DB session."""
    return AuthService(db)


def get_step3_auth_service(db: Session = Depends(get_db)) -> Step3AuthService:
    """Provide Step3AuthService (회원가입/로그인)."""
    return Step3AuthService(db)


def get_step3_goal_service(db: Session = Depends(get_db)) -> Step3GoalService:
    """Provide Step3GoalService (목표 CRUD)."""
    return Step3GoalService(db)


def get_goal_service(db: Session = Depends(get_db)) -> "GoalService":
    """Provide GoalService with an injected DB session."""
    from app.services.goal_service import GoalService

    return GoalService(db)


def get_agent_service(db: Session = Depends(get_db)) -> "AgentService":
    """Provide AgentService with an injected DB session."""
    from app.services.agent_service import AgentService

    return AgentService(db)


def get_mission_service(db: Session = Depends(get_db)) -> "MissionService":
    from app.services.mission_service import MissionService

    return MissionService(db)


def get_timeline_service(db: Session = Depends(get_db)) -> "TimelineService":
    from app.services.timeline_service import TimelineService

    return TimelineService(db)


def get_period_roadmap_service(db: Session = Depends(get_db)) -> "PeriodRoadmapService":
    from app.services.period_roadmap_service import PeriodRoadmapService

    return PeriodRoadmapService(db)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Validate JWT and return the authenticated user.

    Used as: current_user: User = Depends(get_current_user)
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_access_token(token)
        token_data = TokenPayload(sub=str(payload.get("sub", "")))
        if not token_data.sub:
            raise credentials_exception
        user_id = int(token_data.sub)
    except (JWTError, ValueError):
        raise credentials_exception from None

    user = db.query(User).filter(User.id == user_id).first()
    if user is None or not user.is_active:
        raise credentials_exception

    return user
