"""
LangGraph pipeline builder — wires Goal → Planner → Memory agents.

Flow:
    START → memory_load → goal_analyze → planner → memory_save → END
"""

from langgraph.graph import END, START, StateGraph
from sqlalchemy.orm import Session

from app.agents.goal_agent.node import run_goal_agent
from app.agents.memory_agent.node import make_memory_load_node, make_memory_save_node
from app.agents.planner_agent.node import run_planner_agent
from app.agents.shared.state import GrowthCoachState


def build_growth_coach_graph(db: Session):
    """
    Compile the multi-agent graph with DB-injected memory nodes.

    Returns a compiled graph ready for .invoke(initial_state).
    """
    graph = StateGraph(GrowthCoachState)

    graph.add_node("memory_load", make_memory_load_node(db))
    graph.add_node("goal_analyze", run_goal_agent)
    graph.add_node("planner", run_planner_agent)
    graph.add_node("memory_save", make_memory_save_node(db))

    graph.add_edge(START, "memory_load")
    graph.add_edge("memory_load", "goal_analyze")
    graph.add_edge("goal_analyze", "planner")
    graph.add_edge("planner", "memory_save")
    graph.add_edge("memory_save", END)

    return graph.compile()
