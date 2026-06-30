"""Generate 30 days of synthetic tasks, events, and habits for demo.

Includes guaranteed pitch scenarios:
- Double-booking within the next 7 days
- Missed (overdue) deadlines
- Approaching deadlines within 48 hours
- Upcoming high-stakes meeting with prior notes
- Habits with mixed streak health
"""

import random
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.config import get_settings
from app.db.models import AgentLog, Event, Habit, Task, TaskStatus, User
from app.db.session import SessionLocal, init_db
from app.services.prioritization import PrioritizationEngine

TASK_TITLES = [
    "Review pull request #142",
    "Prepare client demo",
    "Update project roadmap",
    "Write unit tests for auth module",
    "Draft blog post on AI productivity",
    "Research competitor features",
    "Organize team offsite agenda",
    "Complete security audit checklist",
    "Send follow-up email to vendor",
    "Update documentation for API v2",
    "Plan sprint retrospective",
]

EVENT_TITLES = [
    "Daily standup",
    "Sprint planning",
    "Design review",
    "Engineering all-hands",
    "Product roadmap review",
    "1:1 with Sarah",
    "Demo day rehearsal",
    "Budget review meeting",
]

HABIT_NAMES = [
    "Morning planning (10 min)",
    "Inbox zero check",
    "End-of-day review",
    "Weekly goal setting",
]


def _round_to_hour(dt: datetime) -> datetime:
    return dt.replace(minute=0, second=0, microsecond=0)


def _seed_pitch_scenarios(db, user: User, now: datetime) -> dict:
    """Deterministic scenarios guaranteed to trigger agent rescue actions."""
    tomorrow = _round_to_hour(now + timedelta(days=1)).replace(hour=10)
    conflict_end = tomorrow + timedelta(hours=1)

    # Scenario 1: Double-booking — two meetings overlap tomorrow at 10 AM
    db.add(
        Event(
            user_id=user.id,
            title="Client sync — Acme Corp",
            description="Quarterly review with Acme stakeholders.",
            start_time=tomorrow,
            end_time=conflict_end,
            location="Teams",
            attendees="demo.user@example.com, client@acme.example.com",
            meeting_notes="Last time: discussed timeline slip; client wants v2 by end of month.",
        )
    )
    db.add(
        Event(
            user_id=user.id,
            title="Architecture review — Platform team",
            description="Conflicts with client sync — classic double-book.",
            start_time=tomorrow + timedelta(minutes=30),
            end_time=tomorrow + timedelta(hours=1, minutes=30),
            location="Zoom",
            attendees="demo.user@example.com, eng-lead@example.com",
            has_conflict=True,
        )
    )

    # Scenario 2: High-stakes meeting soon — triggers meeting prep
    prep_start = _round_to_hour(now + timedelta(hours=3))
    db.add(
        Event(
            user_id=user.id,
            title="Q2 Board Review",
            description="Executive readout — prep critical.",
            start_time=prep_start,
            end_time=prep_start + timedelta(hours=1),
            location="Conference Room A",
            attendees="demo.user@example.com, ceo@example.com, cfo@example.com",
            meeting_notes=(
                "Previous board meeting: flagged revenue miss in APAC. "
                "CFO asked for updated forecast. Action: bring revised deck + risk mitigations."
            ),
        )
    )

    # Scenario 3: Missed deadline (overdue)
    db.add(
        Task(
            user_id=user.id,
            title="Submit expense report",
            description="Overdue — Q1 travel expenses not submitted.",
            status=TaskStatus.IN_PROGRESS,
            due_date=now - timedelta(days=2),
            estimated_minutes=45,
            source="synthetic",
        )
    )
    db.add(
        Task(
            user_id=user.id,
            title="Complete security audit checklist",
            description="Missed internal compliance deadline.",
            status=TaskStatus.BLOCKED,
            due_date=now - timedelta(hours=6),
            estimated_minutes=120,
            source="synthetic",
        )
    )

    # Scenario 4: Approaching deadlines (within 48h) — triggers draft extension emails
    db.add(
        Task(
            user_id=user.id,
            title="Finalize Q2 presentation deck",
            description="Board review dependency — due tomorrow.",
            status=TaskStatus.IN_PROGRESS,
            due_date=now + timedelta(hours=20),
            estimated_minutes=180,
            source="synthetic",
        )
    )
    db.add(
        Task(
            user_id=user.id,
            title="Fix critical bug in checkout flow",
            description="Production blocker — P0 client impact.",
            status=TaskStatus.TODO,
            due_date=now + timedelta(hours=8),
            estimated_minutes=90,
            source="synthetic",
        )
    )

    # Scenario 5: Habits — one thriving, one broken streak
    db.add(
        Habit(
            user_id=user.id,
            name=HABIT_NAMES[0],
            frequency="daily",
            streak=12,
            last_completed=now - timedelta(hours=8),
        )
    )
    db.add(
        Habit(
            user_id=user.id,
            name=HABIT_NAMES[1],
            frequency="daily",
            streak=0,
            last_completed=now - timedelta(days=5),
        )
    )
    db.add(
        Habit(
            user_id=user.id,
            name=HABIT_NAMES[2],
            frequency="daily",
            streak=3,
            last_completed=now - timedelta(days=1),
        )
    )
    db.add(
        Habit(
            user_id=user.id,
            name=HABIT_NAMES[3],
            frequency="weekly",
            streak=6,
            last_completed=now - timedelta(days=2),
        )
    )

    return {
        "double_booking": {
            "when": tomorrow.isoformat(),
            "events": ["Client sync — Acme Corp", "Architecture review — Platform team"],
        },
        "meeting_prep": {"event": "Q2 Board Review", "when": prep_start.isoformat()},
        "missed_deadlines": ["Submit expense report", "Complete security audit checklist"],
        "approaching_deadlines": ["Finalize Q2 presentation deck", "Fix critical bug in checkout flow"],
        "habits": len(HABIT_NAMES),
    }


def _seed_background_month(db, user: User, now: datetime) -> None:
    """Fill the rest of the 30-day window with realistic background noise."""
    start = now - timedelta(days=15)
    end = now + timedelta(days=15)

    for day_offset in range(30):
        day = start + timedelta(days=day_offset)
        for _ in range(random.randint(1, 3)):
            due = day + timedelta(hours=random.randint(9, 17))
            db.add(
                Task(
                    user_id=user.id,
                    title=random.choice(TASK_TITLES),
                    description="Synthetic background task — no real PII.",
                    status=random.choice(list(TaskStatus)),
                    due_date=due if random.random() > 0.25 else None,
                    estimated_minutes=random.choice([15, 30, 60, 90]),
                    source="synthetic",
                )
            )

    current = start
    while current < end:
        if random.random() > 0.35:
            hour = random.randint(8, 17)
            start_time = current.replace(hour=hour, minute=0, second=0, microsecond=0)
            if start_time < now - timedelta(days=1):
                current += timedelta(days=1)
                continue
            end_time = start_time + timedelta(minutes=random.choice([30, 60]))
            db.add(
                Event(
                    user_id=user.id,
                    title=random.choice(EVENT_TITLES),
                    description="Background calendar event.",
                    start_time=start_time,
                    end_time=end_time,
                    location=random.choice(["Teams", "Zoom", None]),
                    attendees="demo.user@example.com",
                )
            )
        current += timedelta(days=1)


def seed() -> None:
    """Populate database with one month of synthetic data + pitch scenarios."""
    settings = get_settings()
    init_db()
    db = SessionLocal()

    try:
        db.query(Task).delete()
        db.query(Event).delete()
        db.query(Habit).delete()
        db.query(AgentLog).delete()
        db.query(User).delete()
        db.commit()

        user = User(
            email=settings.user_email,
            display_name="Demo User",
            calendar_provider=settings.calendar_provider,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        now = datetime.utcnow()
        scenarios = _seed_pitch_scenarios(db, user, now)
        _seed_background_month(db, user, now)
        db.commit()

        prioritizer = PrioritizationEngine(db)
        for task in db.query(Task).filter(Task.user_id == user.id).all():
            prioritizer.prioritize_task(task)
        db.commit()

        task_count = db.query(Task).filter(Task.user_id == user.id).count()
        event_count = db.query(Event).filter(Event.user_id == user.id).count()
        habit_count = db.query(Habit).filter(Habit.user_id == user.id).count()

        print(f"Seeded user '{user.email}':")
        print(f"  {task_count} tasks | {event_count} events | {habit_count} habits")
        print("\nPitch scenarios ready:")
        print(f"  Double-booking: {scenarios['double_booking']['events']}")
        print(f"  Meeting prep:   {scenarios['meeting_prep']['event']}")
        print(f"  Missed:         {scenarios['missed_deadlines']}")
        print(f"  Approaching:    {scenarios['approaching_deadlines']}")
        print('\nRun: POST /v1/agent/run  or click "Save My Day" in the dashboard.')
    finally:
        db.close()


if __name__ == "__main__":
    seed()
