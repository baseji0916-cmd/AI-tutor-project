"""Future Simulation Agent — achievement probability and scenarios."""

from langchain_core.messages import HumanMessage, SystemMessage

from app.agents.shared.llm import get_chat_model
from app.agents.shared.mock import mock_future_simulation
from app.agents.shared.schemas_extended import FutureSimulationOutput

SIMULATION_SYSTEM = """You are the Future Simulation Agent for GrowthPilot.
Predict achievement probability, expected completion date, required effort.
Provide exactly 3 scenarios: A (current pace), B (improved effort), C (reduced scope).
Respond in Korean for descriptions."""


def run_future_simulation_agent(
    goal_title: str,
    start_date: str,
    end_date: str,
    progress_rate: float,
    realism_score: float,
) -> FutureSimulationOutput:
    llm = get_chat_model()
    if llm is None:
        return mock_future_simulation(goal_title, end_date)

    structured = llm.with_structured_output(FutureSimulationOutput)
    prompt = f"""Goal: {goal_title}
Period: {start_date} to {end_date}
Progress: {progress_rate}%
Realism score: {realism_score}
"""
    return structured.invoke(
        [SystemMessage(content=SIMULATION_SYSTEM), HumanMessage(content=prompt)]
    )
