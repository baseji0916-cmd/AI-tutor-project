"""
OpenAI service exceptions.

Each exception maps to a specific failure mode so routers
can return the correct HTTP status code to clients.
"""


class OpenAIServiceError(Exception):
    """Base class for all OpenAI service errors."""

    def __init__(self, message: str, status_code: int = 500) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class OpenAIKeyMissingError(OpenAIServiceError):
    """Raised when OPENAI_API_KEY is not set in environment."""

    def __init__(self, message: str = "OPENAI_API_KEY is not configured") -> None:
        super().__init__(message, status_code=503)


class OpenAITimeoutError(OpenAIServiceError):
    """Raised when OpenAI API does not respond within the timeout."""

    def __init__(self, message: str = "OpenAI API request timed out") -> None:
        super().__init__(message, status_code=504)


class OpenAIRateLimitError(OpenAIServiceError):
    """Raised when OpenAI returns HTTP 429 (rate limit exceeded)."""

    def __init__(self, message: str = "OpenAI API rate limit exceeded") -> None:
        super().__init__(message, status_code=429)


class OpenAICallError(OpenAIServiceError):
    """Raised for general OpenAI API failures (network, auth, server errors)."""

    def __init__(self, message: str, status_code: int = 502) -> None:
        super().__init__(message, status_code=status_code)
