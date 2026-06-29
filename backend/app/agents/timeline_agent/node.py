"""Timeline Agent — growth story from timeline events."""

from langchain_core.messages import HumanMessage, SystemMessage

from app.agents.shared.llm import get_chat_model
from app.agents.shared.mock import mock_growth_story
from app.agents.shared.schemas_extended import GrowthStoryOutput

TIMELINE_SYSTEM = """You are the Timeline Agent for GrowthPilot.
Write an inspiring growth story from the user's timeline events.
Respond in Korean as a narrative story (3-5 paragraphs)."""


def run_timeline_agent(
    user_name: str,
    events_text: str,
    growth_score: float,
) -> GrowthStoryOutput:
    llm = get_chat_model()
    event_count = events_text.count("\n") + 1 if events_text else 0
    if llm is None:
        return mock_growth_story(user_name, event_count)

    structured = llm.with_structured_output(GrowthStoryOutput)
    prompt = f"""User: {user_name}
Growth Score: {growth_score}

Timeline events:
{events_text or 'No events yet'}
"""
    return structured.invoke(
        [SystemMessage(content=TIMELINE_SYSTEM), HumanMessage(content=prompt)]
    )
