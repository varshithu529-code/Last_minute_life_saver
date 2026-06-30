"""LangGraph-powered autonomous productivity agent."""

from datetime import datetime

from sqlalchemy.orm import Session

from app.db.models import AgentLog
from app.services.agent.graph import PITCH_TAGLINE, build_agent_graph
from app.services.agent.llm import chat
from app.services.agent.tools import AgentTools

__all__ = ["AutonomousAgent", "PITCH_TAGLINE"]


class AutonomousAgent:
    """Facade over LangGraph workflow and individual agent tools."""

    def __init__(self, db: Session, user_id: int = 1) -> None:
        self.db = db
        self.user_id = user_id
        self.tools = AgentTools(db, user_id)
        self.graph = build_agent_graph(self.tools)

    def detect_conflicts(self) -> list[dict]:
        return self.tools.detect_conflicts()

    def propose_reschedule(self, event_id: int) -> dict:
        return self.tools.propose_reschedule(event_id)

    def execute_reschedule(self, event_id: int, new_start: datetime) -> dict:
        return self.tools.execute_reschedule(event_id, new_start)

    def deadline_rescue(self) -> list[dict]:
        return self.tools.deadline_rescue()

    def meeting_prep(self, event_id: int) -> dict:
        return self.tools.meeting_prep(event_id)

    def chat(self, message: str) -> dict:
        """Chat with LLM using live agent context."""
        context = self.tools.get_chat_context()
        return chat(message, context=context)

    def handle_intent(self, message: str) -> dict:
        """Detect chat intent and run targeted agent actions; return cards + reply."""
        from app.db.models import Event

        from app.services.agent.cards import build_action_cards, build_proactive_reply

        lower = message.lower()
        cards: list[dict] = []
        actions_taken: list[str] = []

        run_all = any(k in lower for k in ["save my day", "save me", "run everything", "full rescue"])
        wants_conflict = run_all or any(k in lower for k in ["conflict", "resolve", "double-book", "reschedule"])
        wants_deadline = run_all or any(k in lower for k in ["deadline", "rescue", "extension", "overdue", "expense"])
        wants_prep = run_all or any(k in lower for k in ["prep", "meeting", "board"])

        if run_all:
            result = self.run_workflow_demo()
            cards = build_action_cards(result)
            actions_taken = [c["type"] for c in cards]
            llm = self.chat(message)
            return {
                "reply": build_proactive_reply(message, cards, llm["reply"]),
                "confidence": llm["confidence"],
                "actions_taken": actions_taken,
                "action_cards": cards,
                "summary": result.get("summary"),
            }

        if wants_conflict:
            conflicts = self.detect_conflicts()
            if conflicts:
                event_id = conflicts[0]["event_b"]["id"]
                proposal = self.propose_reschedule(event_id)
                from datetime import datetime

                executed = None
                if "proposed_start" in proposal:
                    executed = self.execute_reschedule(
                        event_id, datetime.fromisoformat(proposal["proposed_start"])
                    )
                cards.extend(
                    build_action_cards(
                        {
                            "conflicts": conflicts,
                            "reschedule_proposals": [proposal],
                            "reschedule_executed": executed,
                        }
                    )
                )
                actions_taken.append("conflict")

        if wants_deadline:
            rescues = self.deadline_rescue()
            cards.extend(build_action_cards({"deadline_rescue": rescues}))
            if rescues:
                actions_taken.append("deadline")

        if wants_prep:
            upcoming = (
                self.db.query(Event)
                .filter(Event.user_id == self.user_id, Event.start_time >= datetime.utcnow())
                .order_by(Event.start_time)
                .all()
            )
            target = next((e for e in upcoming if e.meeting_notes), upcoming[0] if upcoming else None)
            if target:
                prep = self.meeting_prep(target.id)
                cards.extend(build_action_cards({"meeting_prep": [prep]}))
                actions_taken.append("prep")

        llm = self.chat(message)
        return {
            "reply": build_proactive_reply(message, cards, llm["reply"]),
            "confidence": llm["confidence"],
            "actions_taken": actions_taken,
            "action_cards": cards,
        }

    def get_metrics(self) -> dict:
        """Impact metrics + gamification layer for dashboard snapshot."""
        from app.db.models import Habit

        logs = self.db.query(AgentLog).filter(AgentLog.user_id == self.user_id).all()
        conflicts = sum(1 for log in logs if log.action_type == "reschedule_executed")
        deadlines = sum(1 for log in logs if log.action_type == "deadline_rescue")
        preps = sum(1 for log in logs if log.action_type == "meeting_prep")

        habits = self.db.query(Habit).filter(Habit.user_id == self.user_id).all()
        streak = max((h.streak for h in habits), default=0)

        focus = min(
            100,
            60 + conflicts * 8 + min(deadlines, 10) * 3 + preps * 5 + min(streak, 14) * 2,
        )

        return {
            "conflicts_resolved": conflicts,
            "deadlines_rescued": deadlines,
            "meetings_prepped": preps,
            "focus_score": focus,
            "streak_days": streak,
        }

    def run_workflow_demo(self, auto_execute_reschedule: bool = True) -> dict:
        """Invoke the compiled LangGraph rescue workflow."""
        initial_state = {
            "user_id": self.user_id,
            "auto_execute_reschedule": auto_execute_reschedule,
            "conflicts": [],
            "reschedule_proposals": [],
            "reschedule_executed": None,
            "deadline_rescue": [],
            "meeting_prep": [],
            "narrative": [],
            "tagline": PITCH_TAGLINE,
            "deadline_summary": {"missed": 0, "approaching": 0},
            "summary": {"conflicts_resolved": 0, "deadlines_rescued": 0, "meetings_prepped": 0},
        }
        return self.graph.invoke(initial_state)
