"""Auto Replanner Agent — revises plans after mission/goal failure."""

import json

from langchain_core.messages import HumanMessage, SystemMessage

from app.agents.shared.llm import get_chat_model
from app.agents.shared.mock import mock_replanner_output
from app.agents.shared.prompts import REPLANNER_AGENT_SYSTEM, coach_personality_hint
from app.agents.shared.schemas_extended import ReplannerOutput


def run_replanner_agent(
    goal_title: str,
    goal_description: str,
    start_date: str,
    end_date: str,
    failure_summary: str,
    improvements: list[str],
    coach_personality: str = "teacher",
    existing_plans_summary: str = "",
) -> ReplannerOutput:
    """
    Generate revised monthly/weekly/daily plans after a failure.

    Used by Auto Replanner flow and failure recovery pipeline.
    """
    llm = get_chat_model()
    if llm is None:
        return mock_replanner_output(goal_title, start_date, end_date, failure_summary)

    structured = llm.with_structured_output(ReplannerOutput)
    context = {
        "goal_title": goal_title,
        "goal_description": goal_description,
        "start_date": start_date,
        "end_date": end_date,
        "failure_summary": failure_summary,
        "improvements": improvements,
        "existing_plans": existing_plans_summary or "None",
    }
    prompt = f"""Coach style: {coach_personality_hint(coach_personality)}

Failure recovery context:
{json.dumps(context, ensure_ascii=False, indent=2)}
"""
    return structured.invoke(
        [SystemMessage(content=REPLANNER_AGENT_SYSTEM), HumanMessage(content=prompt)]
    )
