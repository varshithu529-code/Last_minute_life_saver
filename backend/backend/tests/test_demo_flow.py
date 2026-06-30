"""Guardrails and pitch demo flow tests."""

from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient

from app.db.models import Event, Task, TaskStatus, User
from app.services.agent import AutonomousAgent, PITCH_TAGLINE


@pytest.fixture
def pitch_user(db_session):
    user = User(email="pitch@example.com", display_name="Pitch User")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def _seed_double_book(db, user_id: int, start: datetime) -> None:
    end = start + timedelta(hours=1)
    db.add(Event(user_id=user_id, title="Client sync", start_time=start, end_time=end))
    db.add(
        Event(
            user_id=user_id,
            title="Architecture review",
            start_time=start + timedelta(minutes=30),
            end_time=end + timedelta(minutes=30),
        )
    )
    db.commit()


def test_pitch_workflow_double_booking_and_reschedule(db_session, pitch_user):
    now = datetime.utcnow()
    _seed_double_book(db_session, pitch_user.id, now + timedelta(hours=2))

    agent = AutonomousAgent(db_session, user_id=pitch_user.id)
    result = agent.run_workflow_demo(auto_execute_reschedule=True)

    assert result["tagline"] == PITCH_TAGLINE
    assert len(result["conflicts"]) >= 1
    assert len(result["reschedule_proposals"]) >= 1
    assert result["reschedule_executed"] is not None
    assert result["summary"]["conflicts_resolved"] == 1
    assert any(s["title"] == "Double-booking detected" for s in result["narrative"])


def test_pitch_workflow_missed_and_approaching_deadlines(db_session, pitch_user):
    now = datetime.utcnow()
    db_session.add(
        Task(
            user_id=pitch_user.id,
            title="Overdue expense report",
            status=TaskStatus.IN_PROGRESS,
            due_date=now - timedelta(days=1),
        )
    )
    db_session.add(
        Task(
            user_id=pitch_user.id,
            title="Board deck due soon",
            status=TaskStatus.TODO,
            due_date=now + timedelta(hours=12),
        )
    )
    db_session.commit()

    agent = AutonomousAgent(db_session, user_id=pitch_user.id)
    rescues = agent.deadline_rescue()

    types = {r["rescue_type"] for r in rescues}
    assert "missed_deadline" in types
    assert "approaching_deadline" in types
    assert all("draft_email" in r for r in rescues)
    assert all(r["confidence"] > 0 for r in rescues)


def test_agent_run_endpoint_returns_narrative(client, pitch_user, db_session):
    now = datetime.utcnow()
    _seed_double_book(db_session, pitch_user.id, now + timedelta(hours=1))
    db_session.add(
        Task(
            user_id=pitch_user.id,
            title="Critical deliverable",
            due_date=now - timedelta(hours=3),
            status=TaskStatus.BLOCKED,
        )
    )
    db_session.commit()

    resp = client.post(f"/v1/agent/run?user_id={pitch_user.id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["tagline"] == PITCH_TAGLINE
    assert "narrative" in data
    assert len(data["narrative"]) >= 2
    assert data["deadline_summary"]["missed"] >= 1
