"""
Planner Agent node — generates monthly, weekly plans and daily missions.
"""

import json

from langchain_core.messages import HumanMessage, SystemMessage

from app.agents.shared.llm import get_chat_model
from app.agents.shared.mock import mock_planner_output
from app.agents.shared.prompts import PLANNER_AGENT_SYSTEM, coach_personality_hint
from app.agents.shared.schemas import PlannerOutput
from app.agents.shared.state import GrowthCoachState


def run_planner_agent(state: GrowthCoachState) -> dict:
    """
    LangGraph node: create plans based on goal analysis from Goal Agent.
    """
    llm = get_chat_model()
    personality = state.get("coach_personality", "teacher")

    if llm is None:
        output = mock_planner_output(
            state["goal_title"],
            state["start_date"],
            state["end_date"],
        )
    else:
        structured_llm = llm.with_structured_output(PlannerOutput)
        context = {
            "goal_title": state["goal_title"],
            "goal_description": state.get("goal_description"),
            "start_date": state["start_date"],
            "end_date": state["end_date"],
            "realism_score": state.get("realism_score"),
            "realism_analysis": state.get("realism_analysis"),
            "sub_goals": state.get("sub_goals", []),
            "recommendations": state.get("recommendations", []),
        }
        user_prompt = f"""Coach style: {coach_personality_hint(personality)}

Goal analysis context:
{json.dumps(context, ensure_ascii=False, indent=2)}
"""
        output = structured_llm.invoke(
            [
                SystemMessage(content=PLANNER_AGENT_SYSTEM),
                HumanMessage(content=user_prompt),
            ]
        )

    plans = [
        {
            "plan_type": output.monthly_plan.plan_type,
            "title": output.monthly_plan.title,
            "content": output.monthly_plan.content,
            "start_date": output.monthly_plan.start_date,
            "end_date": output.monthly_plan.end_date,
        },
        {
            "plan_type": output.weekly_plan.plan_type,
            "title": output.weekly_plan.title,
            "content": output.weekly_plan.content,
            "start_date": output.weekly_plan.start_date,
            "end_date": output.weekly_plan.end_date,
        },
    ]
    missions = [
        {
            "title": m.title,
            "description": m.description,
            "scheduled_date": m.scheduled_date,
        }
        for m in output.daily_missions
    ]

    return {
        "plans": plans,
        "daily_missions": missions,
        "current_step": "planner",
    }
