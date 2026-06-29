"""
LangGraph shared state for the Growth Coach multi-agent pipeline.

All agents read/write slices of this TypedDict.
Using total=False so each node returns only the fields it updates.
"""

from typing import TypedDict


class SubGoalState(TypedDict):
    title: str
    description: str


class PlanState(TypedDict):
    plan_type: str
    title: str
    content: str
    start_date: str
    end_date: str


class MissionState(TypedDict):
    title: str
    description: str
    scheduled_date: str


class GrowthCoachState(TypedDict, total=False):
    """
    State flowing through: memory_load → goal_analyze → planner → memory_save.

    Input fields are set by AgentService before graph.invoke().
    """

    # --- Input (from DB / API) ---
    user_id: int
    goal_id: int
    goal_title: str
    goal_description: str
    start_date: str
    end_date: str
    coach_personality: str

    # --- Memory Agent: load ---
    growth_dna_summary: str
    current_growth_score: float
    focus_time_minutes: int

    # --- Goal Agent output ---
    realism_score: float
    realism_analysis: str
    sub_goals: list[SubGoalState]
    recommendations: list[str]
    risks: list[str]

    # --- Planner Agent output ---
    plans: list[PlanState]
    daily_missions: list[MissionState]

    # --- Memory Agent: save ---
    memory_insight: str
    updated_growth_score: float

    # --- Pipeline meta ---
    current_step: str
    error: str

    # --- Failure recovery (Auto Replanner) ---
    failure_summary: str
    failure_improvements: list[str]
    execution_logs_text: str
    existing_plans_summary: str
    revision_summary: str
