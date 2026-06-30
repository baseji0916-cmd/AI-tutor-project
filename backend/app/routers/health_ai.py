"""
AI Health Check router.

Endpoint: GET /api/health/ai
Verifies OpenAI API key and model response.
"""

from fastapi import APIRouter, HTTPException

from app.config.settings import get_settings, reload_settings
from app.services.openai_exceptions import OpenAIServiceError
from app.services.openai_service import OpenAIService

router = APIRouter(prefix="/api/health", tags=["AI Health"])


@router.get("/ai")
def ai_health_check() -> dict[str, str]:
    """
    Test OpenAI API connectivity.

    Success:
        {"status": "success", "message": "OpenAI Connected", ...}

    Failure:
        HTTPException with appropriate status (401, 429, 502, 503, 504)
    """
    reload_settings()
    openai_service = OpenAIService(get_settings())
    try:
        return openai_service.health_check()
    except OpenAIServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc
