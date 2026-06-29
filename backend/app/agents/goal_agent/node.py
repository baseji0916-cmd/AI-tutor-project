"""
Goal Agent node — analyzes goal realism and generates sub-goals.

First LLM step in the pipeline after memory is loaded.
"""

from langchain_core.messages import HumanMessage, SystemMessage

from app.agents.shared.llm import get_chat_model
from app.agents.shared.mock import mock_goal_analysis
from app.agents.shared.prompts import GOAL_AGENT_SYSTEM, coach_personality_hint
from app.agents.shared.schemas import GoalAnalysisOutput
from app.agents.shared.state import GrowthCoachState


def run_goal_agent(state: GrowthCoachState) -> dict:
    """
    LangGraph node: analyze goal and return structured analysis.

    Uses OpenAI when configured; falls back to mock in dev/test.
    """
    llm = get_chat_model()
    personality = state.get("coach_personality", "teacher")

    if llm is None:
        analysis = mock_goal_analysis(
            state["goal_title"],
            state.get("goal_description", ""),
            state["start_date"],
            state["end_date"],
        )
    else:
        structured_llm = llm.with_structured_output(GoalAnalysisOutput)
        user_prompt = f"""Coach style: {coach_personality_hint(personality)}

User Growth DNA context: {state.get("growth_dna_summary", "No prior data")}

Goal:
- Title: {state["goal_title"]}
- Description: {state.get("goal_description") or "None"}
- Period: {state["start_date"]} to {state["end_date"]}
"""
        analysis = structured_llm.invoke(
            [
                SystemMessage(content=GOAL_AGENT_SYSTEM),
                HumanMessage(content=user_prompt),
            ]
        )

    return {
        "realism_score": analysis.realism_score,
        "realism_analysis": analysis.realism_analysis,
        "sub_goals": [{"title": sg.title, "description": sg.description} for sg in analysis.sub_goals],
        "recommendations": analysis.recommendations,
        "risks": analysis.risks,
        "current_step": "goal_analyze",
    }
