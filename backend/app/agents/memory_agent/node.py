"""
Memory Agent nodes — load and save user Growth DNA.

Unlike other agents, load/save interact with the database via injected session.
"""

import json

from langchain_core.messages import HumanMessage, SystemMessage
from sqlalchemy.orm import Session

from app.agents.shared.llm import get_chat_model
from app.agents.shared.mock import mock_memory_update
from app.agents.shared.prompts import MEMORY_AGENT_SYSTEM, coach_personality_hint
from app.agents.shared.schemas import MemoryUpdateOutput
from app.agents.shared.state import GrowthCoachState
from app.infrastructure.database.models.growth_dna import GrowthDNA


def make_memory_load_node(db: Session):
    """
    Factory: returns a LangGraph node that loads Growth DNA from SQLite.

    Why factory pattern? LangGraph nodes are plain callables; we inject DB here.
    """

    def memory_load(state: GrowthCoachState) -> dict:
        dna = db.query(GrowthDNA).filter(GrowthDNA.user_id == state["user_id"]).first()
        if not dna:
            return {
                "growth_dna_summary": "New user — no Growth DNA yet.",
                "current_growth_score": 0.0,
                "focus_time_minutes": 0,
                "current_step": "memory_load",
            }

        summary_parts = [
            f"Growth Score: {dna.growth_score}",
            f"Focus time: {dna.focus_time_minutes} min/day",
        ]
        if dna.execution_style:
            summary_parts.append(f"Style: {dna.execution_style}")

        return {
            "growth_dna_summary": " | ".join(summary_parts),
            "current_growth_score": dna.growth_score,
            "focus_time_minutes": dna.focus_time_minutes,
            "current_step": "memory_load",
        }

    return memory_load


def make_memory_save_node(db: Session):
    """Factory: LLM-powered Growth DNA update + persist to database."""

    def memory_save(state: GrowthCoachState) -> dict:
        llm = get_chat_model()
        personality = state.get("coach_personality", "teacher")
        realism = state.get("realism_score", 50.0)

        if llm is None:
            update = mock_memory_update(realism, personality)
        else:
            structured_llm = llm.with_structured_output(MemoryUpdateOutput)
            user_prompt = f"""Coach style: {coach_personality_hint(personality)}

Current Growth Score: {state.get("current_growth_score", 0)}
Goal realism score: {realism}
Goal: {state.get("goal_title")}
Analysis: {state.get("realism_analysis", "")}
Plans created: {len(state.get("plans", []))} plans, {len(state.get("daily_missions", []))} missions
"""
            update = structured_llm.invoke(
                [
                    SystemMessage(content=MEMORY_AGENT_SYSTEM),
                    HumanMessage(content=user_prompt),
                ]
            )

        dna = db.query(GrowthDNA).filter(GrowthDNA.user_id == state["user_id"]).first()
        if dna:
            dna.focus_time_minutes = update.focus_time_minutes
            dna.failure_patterns = json.dumps(update.failure_patterns, ensure_ascii=False)
            dna.success_patterns = json.dumps(update.success_patterns, ensure_ascii=False)
            dna.execution_style = json.dumps(
                {"style": update.execution_style},
                ensure_ascii=False,
            )
            dna.growth_score = max(0.0, dna.growth_score + update.growth_score_delta)
            db.add(dna)
            db.commit()
            db.refresh(dna)
            new_score = dna.growth_score
        else:
            new_score = update.growth_score_delta

        return {
            "memory_insight": update.insight,
            "updated_growth_score": new_score,
            "current_step": "memory_save",
        }

    return memory_save
