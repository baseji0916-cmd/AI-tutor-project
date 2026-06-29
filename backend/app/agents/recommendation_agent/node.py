"""Recommendation Agent — goals, books, skills, habits."""

from langchain_core.messages import HumanMessage, SystemMessage

from app.agents.shared.llm import get_chat_model
from app.agents.shared.mock import mock_recommendations
from app.agents.shared.schemas_extended import RecommendationOutput

RECOMMENDATION_SYSTEM = """You are the Recommendation Agent for GrowthPilot.
Suggest personalized goals, books, skills, and habits based on user profile.
Respond in Korean."""


def run_recommendation_agent(
    goals_summary: str,
    dna_summary: str,
    coach_personality: str,
) -> RecommendationOutput:
    llm = get_chat_model()
    if llm is None:
        return mock_recommendations()

    structured = llm.with_structured_output(RecommendationOutput)
    prompt = f"""Coach: {coach_personality}
Active goals: {goals_summary}
Growth DNA: {dna_summary}
"""
    return structured.invoke(
        [SystemMessage(content=RECOMMENDATION_SYSTEM), HumanMessage(content=prompt)]
    )
