"""OpenAI health check and service tests."""

from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from app.services.openai_exceptions import OpenAIKeyMissingError
from app.services.openai_service import OpenAIService


def test_ai_health_success(client: TestClient) -> None:
    mock_result = {
        "status": "success",
        "message": "OpenAI Connected",
        "model": "gpt-4o-mini",
        "reply": "Connected",
    }
    with patch.object(OpenAIService, "health_check", return_value=mock_result):
        response = client.get("/api/health/ai")
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert response.json()["message"] == "OpenAI Connected"


def test_ai_health_missing_key(client: TestClient) -> None:
    with patch.object(
        OpenAIService,
        "health_check",
        side_effect=OpenAIKeyMissingError(),
    ):
        response = client.get("/api/health/ai")
    assert response.status_code == 503


def test_openai_service_chat() -> None:
    """Unit test chat() with mocked OpenAI client (no network)."""
    service = OpenAIService()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="Hello"))]

    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response

    with patch.object(service, "get_client", return_value=mock_client):
        assert service.chat("Hi") == "Hello"
