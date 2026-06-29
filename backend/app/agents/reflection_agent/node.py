"""Reflection Agent — analyzes mission/goal failures."""

from langchain_core.messages import HumanMessage, SystemMessage

from app.agents.shared.llm import get_chat_model
from app.agents.shared.mock import mock_failure_analysis
from app.agents.shared.schemas_extended import FailureAnalysisOutput

REFLECTION_SYSTEM = """You are the Reflection Agent for GrowthPilot.
Analyze why the user failed a mission or goal. Identify root causes, patterns, and improvements.
Respond in the same language as the mission title (Korean if Korean)."""


def run_reflection_agent(
    mission_title: str,
    mission_description: str,
    goal_title: str,
    failure_notes: str = "",
    execution_logs_text: str = "",
) -> FailureAnalysisOutput:
    llm = get_chat_model()
    if llm is None:
        return mock_failure_analysis(mission_title)

    structured = llm.with_structured_output(FailureAnalysisOutput)
    prompt = f"""Mission: {mission_title}
Description: {mission_description or 'None'}
Related goal: {goal_title}
User notes: {failure_notes or 'None'}
Execution history:
{execution_logs_text or 'No logs'}
"""
    return structured.invoke(
        [SystemMessage(content=REFLECTION_SYSTEM), HumanMessage(content=prompt)]
    )
