"""Coach Agent — personality-aware coaching feedback."""

from langchain_core.messages import HumanMessage, SystemMessage

from app.agents.shared.llm import get_chat_model
from app.agents.shared.mock import mock_coach_feedback
from app.agents.shared.prompts import coach_personality_hint
from app.agents.shared.schemas_extended import CoachFeedbackOutput

COACH_SYSTEM = """You are the Coach Agent for GrowthPilot.
Generate coaching feedback that matches the user's chosen personality.
The coaching STRATEGY must change per personality, not just the tone.
Respond in Korean unless context is English."""


def run_coach_agent(
    personality: str,
    context: str,
    stats_summary: str = "",
) -> CoachFeedbackOutput:
    llm = get_chat_model()
    if llm is None:
        return mock_coach_feedback(personality, context)

    structured = llm.with_structured_output(CoachFeedbackOutput)
    prompt = f"""Coach personality: {personality}
Style hint: {coach_personality_hint(personality)}

User stats: {stats_summary or 'No stats'}

Context:
{context}
"""
    return structured.invoke(
        [SystemMessage(content=COACH_SYSTEM), HumanMessage(content=prompt)]
    )
