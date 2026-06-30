"""LangGraph agent state — shared across workflow nodes."""

from typing import TypedDict


class AgentState(TypedDict, total=False):
    """State passed between LangGraph nodes during the rescue workflow."""

    user_id: int
    auto_execute_reschedule: bool
    conflicts: list[dict]
    reschedule_proposals: list[dict]
    reschedule_executed: dict | None
    deadline_rescue: list[dict]
    meeting_prep: list[dict]
    narrative: list[dict]
    tagline: str
    deadline_summary: dict
    summary: dict
