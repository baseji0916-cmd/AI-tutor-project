"""
OpenAI LLM factory for LangGraph agents.

Delegates to OpenAIService so all GPT calls share one implementation.
"""

from langchain_openai import ChatOpenAI

from app.config.settings import get_settings
from app.services.openai_service import OpenAIService


def get_chat_model() -> ChatOpenAI | None:
    """
    Create LangChain ChatOpenAI for structured agent outputs.

    Returns None in mock mode when API key is not configured.
    """
    service = OpenAIService()
    if not service.is_configured():
        return None

    settings = get_settings()
    return ChatOpenAI(
        api_key=settings.openai_api_key,
        model=settings.openai_model,
        temperature=0.7,
        timeout=settings.openai_timeout_seconds,
        max_retries=settings.openai_max_retries,
    )


def is_llm_available() -> bool:
    """True when OpenAI API key is configured."""
    return OpenAIService().is_configured()
