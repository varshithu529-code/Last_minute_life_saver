"""LangGraph state machine for the autonomous productivity workflow."""

from datetime import datetime
from typing import Literal

from langgraph.graph import END, START, StateGraph

from app.services.agent.state import AgentState
from app.services.agent.tools import AgentTools

PITCH_TAGLINE = "This bot doesn't just remind you — it saves you."


def _route_after_conflicts(state: AgentState) -> Literal["propose_reschedule", "deadline_rescue"]:
    return "propose_reschedule" if state.get("conflicts") else "deadline_rescue"


def _route_after_propose(state: AgentState) -> Literal["execute_reschedule", "deadline_rescue"]:
    if state.get("auto_execute_reschedule") and state.get("reschedule_proposals"):
        proposal = state["reschedule_proposals"][0]
        if "proposed_start" in proposal and "error" not in proposal:
            return "execute_reschedule"
    return "deadline_rescue"


def build_agent_graph(tools: AgentTools):
    """Compile the LangGraph workflow: detect → reschedule → rescue → prep."""

    def detect_conflicts_node(state: AgentState) -> dict:
        conflicts = tools.detect_conflicts()
        narrative = list(state.get("narrative") or [])
        narrative.append(
            {
                "step": len(narrative) + 1,
                "title": "Double-booking detected",
                "icon": "calendar",
                "status": "completed" if conflicts else "skipped",
                "detail": (
                    f"Found {len(conflicts)} overlap(s): "
                    f"'{conflicts[0]['event_a']['title']}' vs '{conflicts[0]['event_b']['title']}'"
                    if conflicts
                    else "No conflicts in the next 7 days."
                ),
            }
        )
        return {"conflicts": conflicts, "narrative": narrative}

    def propose_reschedule_node(state: AgentState) -> dict:
        conflicts = state.get("conflicts") or []
        event_id = conflicts[0]["event_b"]["id"]
        proposal = tools.propose_reschedule(event_id)
        narrative = list(state.get("narrative") or [])
        narrative.append(
            {
                "step": len(narrative) + 1,
                "title": "Auto-reschedule proposed",
                "icon": "reschedule",
                "status": "proposed",
                "detail": proposal.get("proposal", ""),
            }
        )
        return {"reschedule_proposals": [proposal], "narrative": narrative}

    def execute_reschedule_node(state: AgentState) -> dict:
        proposal = state["reschedule_proposals"][0]
        event_id = proposal["event_id"]
        new_start = datetime.fromisoformat(proposal["proposed_start"])
        executed = tools.execute_reschedule(event_id, new_start)
        narrative = list(state.get("narrative") or [])
        narrative.append(
            {
                "step": len(narrative) + 1,
                "title": "Reschedule executed",
                "icon": "check",
                "status": "completed",
                "detail": f"Calendar updated via {type(tools.calendar).__name__}. Conflict resolved.",
            }
        )
        return {"reschedule_executed": executed, "narrative": narrative}

    def deadline_rescue_node(state: AgentState) -> dict:
        actions = tools.deadline_rescue()
        missed = [d for d in actions if d["rescue_type"] == "missed_deadline"]
        approaching = [d for d in actions if d["rescue_type"] == "approaching_deadline"]
        narrative = list(state.get("narrative") or [])

        if missed:
            narrative.append(
                {
                    "step": len(narrative) + 1,
                    "title": "Missed deadline rescue",
                    "icon": "alert",
                    "status": "completed",
                    "detail": f"Drafted recovery emails for {len(missed)} overdue task(s).",
                    "items": [{"title": m["title"], "draft": m["draft_email"][:200]} for m in missed[:2]],
                }
            )
        if approaching:
            narrative.append(
                {
                    "step": len(narrative) + 1,
                    "title": "Approaching deadline rescue",
                    "icon": "email",
                    "status": "completed",
                    "detail": f"Drafted extension emails for {len(approaching)} urgent task(s).",
                    "items": [{"title": a["title"], "draft": a["draft_email"][:200]} for a in approaching[:2]],
                }
            )

        return {
            "deadline_rescue": actions,
            "deadline_summary": {"missed": len(missed), "approaching": len(approaching)},
            "narrative": narrative,
        }

    def meeting_prep_node(state: AgentState) -> dict:
        from app.db.models import Event

        events = (
            tools.db.query(Event)
            .filter(Event.user_id == tools.user_id, Event.start_time >= datetime.utcnow())
            .order_by(Event.start_time)
            .all()
        )
        prep_target = next((e for e in events if e.meeting_notes), events[0] if events else None)

        prep_results = []
        narrative = list(state.get("narrative") or [])
        if prep_target:
            prep = tools.meeting_prep(prep_target.id)
            prep_results.append(prep)
            narrative.append(
                {
                    "step": len(narrative) + 1,
                    "title": "Meeting prep assistant",
                    "icon": "prep",
                    "status": "completed",
                    "detail": f"Surfaced prior notes + checklist for '{prep_target.title}'.",
                    "prep_checklist": prep.get("prep_checklist", "")[:300],
                    "previous_notes": prep.get("previous_notes"),
                }
            )

        return {"meeting_prep": prep_results, "narrative": narrative}

    def finalize_node(state: AgentState) -> dict:
        return {
            "tagline": PITCH_TAGLINE,
            "summary": {
                "conflicts_resolved": 1 if state.get("reschedule_executed") else 0,
                "deadlines_rescued": len(state.get("deadline_rescue") or []),
                "meetings_prepped": len(state.get("meeting_prep") or []),
            },
        }

    graph = StateGraph(AgentState)
    graph.add_node("detect_conflicts", detect_conflicts_node)
    graph.add_node("propose_reschedule", propose_reschedule_node)
    graph.add_node("execute_reschedule", execute_reschedule_node)
    graph.add_node("deadline_rescue", deadline_rescue_node)
    graph.add_node("meeting_prep", meeting_prep_node)
    graph.add_node("finalize", finalize_node)

    graph.add_edge(START, "detect_conflicts")
    graph.add_conditional_edges("detect_conflicts", _route_after_conflicts)
    graph.add_conditional_edges("propose_reschedule", _route_after_propose)
    graph.add_edge("execute_reschedule", "deadline_rescue")
    graph.add_edge("deadline_rescue", "meeting_prep")
    graph.add_edge("meeting_prep", "finalize")
    graph.add_edge("finalize", END)

    return graph.compile()
