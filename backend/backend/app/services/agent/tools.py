"""Agent tools — DB/calendar operations invoked by LangGraph nodes."""

import json
import logging
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.core.logging import log_action
from app.db.models import AgentLog, Event, Task, TaskStatus
from app.services.agent.llm import chat, draft_email
from app.services.calendar import CalendarEvent, get_calendar_provider
from app.services.prioritization import PrioritizationEngine

logger = logging.getLogger(__name__)


class AgentTools:
    """Tool layer used by LangGraph nodes and individual API endpoints."""

    def __init__(self, db: Session, user_id: int = 1) -> None:
        self.db = db
        self.user_id = user_id
        self.calendar = get_calendar_provider()
        self.prioritizer = PrioritizationEngine(db)

    def _log(
        self,
        action_type: str,
        description: str,
        confidence: float = 1.0,
        status: str = "completed",
        metadata: dict | None = None,
    ) -> AgentLog:
        entry = AgentLog(
            user_id=self.user_id,
            action_type=action_type,
            description=description,
            confidence=confidence,
            status=status,
            metadata_json=json.dumps(metadata) if metadata else None,
        )
        self.db.add(entry)
        self.db.commit()
        self.db.refresh(entry)
        log_action(logger, action_type, user_id=self.user_id, confidence=confidence)
        return entry

    def detect_conflicts(self) -> list[dict]:
        """Find overlapping calendar events in the next 7 days."""
        now = datetime.utcnow()
        window_end = now + timedelta(days=7)
        events = (
            self.db.query(Event)
            .filter(
                Event.user_id == self.user_id,
                Event.start_time >= now,
                Event.start_time <= window_end,
            )
            .order_by(Event.start_time)
            .all()
        )

        conflicts = []
        for i, a in enumerate(events):
            for b in events[i + 1 :]:
                if a.start_time < b.end_time and b.start_time < a.end_time:
                    a.has_conflict = True
                    b.has_conflict = True
                    conflicts.append(
                        {
                            "event_a": {
                                "id": a.id,
                                "title": a.title,
                                "start": a.start_time.isoformat(),
                            },
                            "event_b": {
                                "id": b.id,
                                "title": b.title,
                                "start": b.start_time.isoformat(),
                            },
                        }
                    )
        self.db.commit()

        if conflicts:
            self._log(
                "conflict_detected",
                f"Found {len(conflicts)} scheduling conflict(s)",
                metadata={"conflicts": conflicts},
            )
        return conflicts

    def propose_reschedule(self, event_id: int) -> dict:
        """Propose a new time slot for a conflicting event."""
        event = self.db.query(Event).filter(Event.id == event_id).first()
        if not event:
            return {"error": "Event not found"}

        proposed_start = event.end_time + timedelta(hours=1)
        proposed_end = proposed_start + (event.end_time - event.start_time)
        proposal = (
            f"Move '{event.title}' to {proposed_start.strftime('%a %b %d, %I:%M %p')} – "
            f"{proposed_end.strftime('%I:%M %p')}"
        )

        log_entry = self._log(
            "reschedule_proposed",
            proposal,
            confidence=0.85,
            status="proposed",
            metadata={"event_id": event_id, "proposed_start": proposed_start.isoformat()},
        )

        return {
            "event_id": event_id,
            "proposal": proposal,
            "proposed_start": proposed_start.isoformat(),
            "proposed_end": proposed_end.isoformat(),
            "log_id": log_entry.id,
        }

    def execute_reschedule(self, event_id: int, new_start: datetime) -> dict:
        """Execute reschedule via calendar provider."""
        event = self.db.query(Event).filter(Event.id == event_id).first()
        if not event:
            return {"error": "Event not found"}

        duration = event.end_time - event.start_time
        new_end = new_start + duration
        cal_event = CalendarEvent(
            title=event.title,
            start=new_start,
            end=new_end,
            external_id=event.external_id,
            location=event.location,
        )

        if event.external_id:
            self.calendar.update_event(event.external_id, cal_event)
        else:
            result = self.calendar.create_event(cal_event)
            event.external_id = result.external_id

        event.start_time = new_start
        event.end_time = new_end
        event.has_conflict = False
        self.db.commit()

        log_entry = self._log(
            "reschedule_executed",
            f"Rescheduled '{event.title}' to {new_start.isoformat()}",
            metadata={"event_id": event_id},
        )
        return {"status": "success", "event_id": event_id, "log_id": log_entry.id}

    def deadline_rescue(self) -> list[dict]:
        """Draft rescue emails for overdue and approaching deadlines."""
        now = datetime.utcnow()
        threshold = now + timedelta(hours=48)

        overdue_tasks = (
            self.db.query(Task)
            .filter(
                Task.user_id == self.user_id,
                Task.status != TaskStatus.DONE,
                Task.due_date.isnot(None),
                Task.due_date < now,
            )
            .all()
        )
        approaching_tasks = (
            self.db.query(Task)
            .filter(
                Task.user_id == self.user_id,
                Task.status != TaskStatus.DONE,
                Task.due_date.isnot(None),
                Task.due_date >= now,
                Task.due_date <= threshold,
            )
            .all()
        )

        results = []
        for task in overdue_tasks + approaching_tasks:
            rescue_type = (
                "missed_deadline" if task.due_date and task.due_date < now else "approaching_deadline"
            )
            self.prioritizer.prioritize_task(task)

            purpose = (
                f"Apologize and request extension for overdue task: {task.title}"
                if rescue_type == "missed_deadline"
                else f"Request extension for task: {task.title}"
            )
            draft = draft_email(
                purpose=purpose,
                recipient="manager@example.com",
                context=f"Due: {task.due_date}, Status: {task.status.value}, Type: {rescue_type}",
            )
            self._log(
                "deadline_rescue",
                f"{'Missed deadline rescue' if rescue_type == 'missed_deadline' else 'Deadline rescue'}: '{task.title}'",
                confidence=draft["confidence"],
                status="proposed",
                metadata={"task_id": task.id, "rescue_type": rescue_type, "draft": draft["reply"][:500]},
            )
            results.append(
                {
                    "task_id": task.id,
                    "title": task.title,
                    "rescue_type": rescue_type,
                    "due_date": task.due_date.isoformat() if task.due_date else None,
                    "hours_overdue": round((now - task.due_date).total_seconds() / 3600, 1)
                    if task.due_date and task.due_date < now
                    else None,
                    "draft_email": draft["reply"],
                    "confidence": draft["confidence"],
                }
            )
        self.db.commit()
        return results

    def meeting_prep(self, event_id: int) -> dict:
        """Surface prior notes and generate a prep checklist via LLM."""
        event = self.db.query(Event).filter(Event.id == event_id).first()
        if not event:
            return {"error": "Event not found"}

        context = (
            f"Meeting: {event.title}\n"
            f"Time: {event.start_time}\n"
            f"Attendees: {event.attendees or 'N/A'}\n"
            f"Previous notes: {event.meeting_notes or 'No prior notes available.'}"
        )
        llm_result = chat(
            "Provide a brief meeting prep checklist based on the context.",
            context=context,
        )
        self._log(
            "meeting_prep",
            f"Generated prep for '{event.title}'",
            confidence=llm_result["confidence"],
            metadata={"event_id": event_id},
        )

        return {
            "event_id": event_id,
            "title": event.title,
            "previous_notes": event.meeting_notes,
            "prep_checklist": llm_result["reply"],
            "confidence": llm_result["confidence"],
        }

    def get_chat_context(self) -> str:
        """Build read-only context for chat — no logging or LLM calls."""
        now = datetime.utcnow()
        window_end = now + timedelta(days=7)

        event_count = (
            self.db.query(Event)
            .filter(
                Event.user_id == self.user_id,
                Event.start_time >= now,
                Event.start_time <= window_end,
            )
            .count()
        )
        overdue = (
            self.db.query(Task)
            .filter(
                Task.user_id == self.user_id,
                Task.status != TaskStatus.DONE,
                Task.due_date.isnot(None),
                Task.due_date < now,
            )
            .count()
        )
        approaching = (
            self.db.query(Task)
            .filter(
                Task.user_id == self.user_id,
                Task.status != TaskStatus.DONE,
                Task.due_date.isnot(None),
                Task.due_date >= now,
                Task.due_date <= now + timedelta(hours=48),
            )
            .count()
        )

        parts = []
        if event_count:
            parts.append(f"Upcoming events (7d): {event_count}")
        if overdue:
            parts.append(f"Overdue tasks: {overdue}")
        if approaching:
            parts.append(f"Tasks due within 48h: {approaching}")
        return "\n".join(parts) if parts else "No urgent issues detected."
