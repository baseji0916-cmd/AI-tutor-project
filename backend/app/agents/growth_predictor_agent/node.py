"""Growth Predictor Agent — calculates goal achievement probability."""

import json

from langchain_core.messages import HumanMessage, SystemMessage

from app.agents.shared.llm import get_chat_model
from app.agents.shared.mock import mock_growth_predictor
from app.agents.shared.prompts import GROWTH_PREDICTOR_SYSTEM, coach_personality_hint
from app.agents.shared.schemas_extended import GrowthPredictorOutput


def run_growth_predictor_agent(
    goal_title: str,
    start_date: str,
    end_date: str,
    progress_rate: float,
    realism_score: float,
    growth_dna_summary: str,
    coach_personality: str = "teacher",
) -> GrowthPredictorOutput:
    """
    Predict achievement probability using progress, timeline, and Growth DNA.

    Distinct from Future Simulation (scenarios A/B/C) — focused on probability forecast.
    """
    llm = get_chat_model()
    if llm is None:
        return mock_growth_predictor(goal_title, end_date, progress_rate, realism_score)

    structured = llm.with_structured_output(GrowthPredictorOutput)
    context = {
        "goal_title": goal_title,
        "start_date": start_date,
        "end_date": end_date,
        "progress_rate": progress_rate,
        "realism_score": realism_score,
        "growth_dna": growth_dna_summary,
    }
    prompt = f"""Coach style: {coach_personality_hint(coach_personality)}

Prediction context:
{json.dumps(context, ensure_ascii=False, indent=2)}
"""
    return structured.invoke(
        [SystemMessage(content=GROWTH_PREDICTOR_SYSTEM), HumanMessage(content=prompt)]
    )
