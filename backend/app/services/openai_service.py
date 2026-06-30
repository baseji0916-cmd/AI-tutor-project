"""
OpenAI Service — centralized GPT client for GrowthPilot.

Used by:
- GET /api/health/ai  (connection check)
- LangGraph agents     (via get_openai_service dependency)
- Future AI features

Design: class-based so LangGraph nodes can inject or share one instance.
"""

from openai import APIConnectionError, APITimeoutError, OpenAI, RateLimitError
from openai import AuthenticationError, OpenAIError

from app.config.settings import Settings, get_settings
from app.services.openai_exceptions import (
    OpenAICallError,
    OpenAIKeyMissingError,
    OpenAIRateLimitError,
    OpenAIServiceError,
    OpenAITimeoutError,
)


class OpenAIService:
    """
    Wraps the official OpenAI Python SDK.

    Responsibilities:
    - Validate API key before calls
    - Execute chat completions
    - Translate SDK errors into domain exceptions
    """

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._client: OpenAI | None = None
        self._client_api_key: str | None = None

    def _reset_client_if_key_changed(self) -> None:
        current_key = self._settings.openai_api_key.strip()
        if self._client is not None and self._client_api_key != current_key:
            self._client = None
        self._client_api_key = current_key

    @property
    def settings(self) -> Settings:
        return self._settings

    @property
    def model(self) -> str:
        return self._settings.openai_model

    def is_configured(self) -> bool:
        """Check if API key is present without making a network call."""
        return self._settings.has_openai_api_key

    def get_client(self) -> OpenAI:
        """
        Lazy-initialize and return the OpenAI client.

        Raises:
            OpenAIKeyMissingError: if OPENAI_API_KEY is empty or placeholder.
        """
        if not self.is_configured():
            raise OpenAIKeyMissingError(
                "OPENAI_API_KEY is missing. Add it to backend/.env."
            )

        self._reset_client_if_key_changed()

        if self._client is None:
            self._client = OpenAI(
                api_key=self._settings.openai_api_key,
                timeout=self._settings.openai_timeout_seconds,
                max_retries=self._settings.openai_max_retries,
            )
        return self._client

    def chat(self, prompt: str, system: str | None = None) -> str:
        """
        Send a chat completion request and return the assistant text.

        Args:
            prompt: User message content.
            system: Optional system instruction.

        Returns:
            Assistant response text.

        Raises:
            OpenAIKeyMissingError, OpenAITimeoutError,
            OpenAIRateLimitError, OpenAICallError
        """
        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        try:
            client = self.get_client()
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
            )
            content = response.choices[0].message.content
            if not content:
                raise OpenAICallError("OpenAI returned an empty response")
            return content.strip()

        except OpenAIKeyMissingError:
            raise
        except APITimeoutError as exc:
            raise OpenAITimeoutError(str(exc)) from exc
        except RateLimitError as exc:
            raise OpenAIRateLimitError(str(exc)) from exc
        except AuthenticationError as exc:
            raise OpenAICallError(f"Invalid OpenAI API key: {exc}", status_code=401) from exc
        except APIConnectionError as exc:
            raise OpenAICallError(f"Cannot connect to OpenAI: {exc}", status_code=502) from exc
        except OpenAIError as exc:
            raise OpenAICallError(f"OpenAI API error: {exc}", status_code=502) from exc
        except OpenAIServiceError:
            raise
        except Exception as exc:
            raise OpenAICallError(f"Unexpected error calling OpenAI: {exc}") from exc

    def health_check(self) -> dict[str, str]:
        """
        Verify OpenAI connectivity with a minimal completion request.

        Returns:
            {"status": "success", "message": "OpenAI Connected", "model": "..."}

        Raises:
            OpenAIServiceError subclasses on any failure.
        """
        reply = self.chat(
            prompt="Reply with exactly one word: Connected",
            system="You are a health-check bot. Follow instructions exactly.",
        )
        return {
            "status": "success",
            "message": "OpenAI Connected",
            "model": self.model,
            "reply": reply,
        }


def get_openai_service() -> OpenAIService:
    """
    FastAPI / LangGraph dependency: returns OpenAIService with current settings.

    Usage:
        service: OpenAIService = Depends(get_openai_service)
    """
    return OpenAIService(get_settings())
