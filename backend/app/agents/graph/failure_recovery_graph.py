"""
Failure recovery LangGraph pipeline.

Flow: reflection (Failure Analyzer) → memory_update → replanner (Auto Replanner)
"""

from langgraph.graph import END, START, StateGraph
from sqlalchemy.orm import Session

from app.agents.replanner_agent.node import run_replanner_agent
from app.agents.shared.state import GrowthCoachState


def _make_reflection_node(failure_summary: str, improvements: list[str], execution_logs: str):
    """Closure: inject failure context into state for replanner."""

    def reflection_node(state: GrowthCoachState) -> dict:
        return {
            "failure_summary": failure_summary,
            "failure_improvements": improvements,
            "execution_logs_text": execution_logs,
            "current_step": "reflection",
        }

    return reflection_node


def _make_replanner_node():
    """LangGraph node wrapping Auto Replanner agent."""

    def replanner_node(state: GrowthCoachState) -> dict:
        output = run_replanner_agent(
            goal_title=state["goal_title"],
            goal_description=state.get("goal_description", ""),
            start_date=state["start_date"],
            end_date=state["end_date"],
            failure_summary=state.get("failure_summary", ""),
            improvements=state.get("failure_improvements", []),
            coach_personality=state.get("coach_personality", "teacher"),
            existing_plans_summary=state.get("existing_plans_summary", ""),
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
            "revision_summary": output.revision_summary,
            "current_step": "replanner",
        }

    return replanner_node


def build_failure_recovery_graph(
    db: Session,
    failure_summary: str,
    improvements: list[str],
    execution_logs: str,
):
    """
    Compile failure recovery graph: reflection context → replanner.

    DNA update is handled by AgentService after graph completes.
    """
    from app.agents.memory_agent.node import make_memory_save_node

    graph = StateGraph(GrowthCoachState)
    graph.add_node("reflection", _make_reflection_node(failure_summary, improvements, execution_logs))
    graph.add_node("replanner", _make_replanner_node())
    graph.add_node("memory_save", make_memory_save_node(db))

    graph.add_edge(START, "reflection")
    graph.add_edge("reflection", "replanner")
    graph.add_edge("replanner", "memory_save")
    graph.add_edge("memory_save", END)

    return graph.compile()
