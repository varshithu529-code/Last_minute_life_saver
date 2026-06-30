"""Backend test suite."""

from datetime import datetime, timedelta

import pytest
from app.db.models import Event, Task, User
from app.services.prioritization import PrioritizationEngine


@pytest.fixture
def demo_user(db_session):
    user = User(email="test@example.com", display_name="Test User")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def test_health_check(client):
    response = client.get("/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ("ok", "degraded")
    assert "version" in data


def test_create_and_list_tasks(client, demo_user):
    payload = {
        "title": "Test task",
        "description": "A test",
        "due_date": (datetime.utcnow() + timedelta(days=1)).isoformat(),
        "estimated_minutes": 45,
    }
    create_resp = client.post(f"/v1/tasks?user_id={demo_user.id}", json=payload)
    assert create_resp.status_code == 201
    task = create_resp.json()
    assert task["title"] == "Test task"
    assert task["ml_score"] >= 0

    list_resp = client.get(f"/v1/tasks?user_id={demo_user.id}")
    assert list_resp.status_code == 200
    assert len(list_resp.json()) >= 1


def test_prioritization_engine(db_session, demo_user):
    task = Task(
        user_id=demo_user.id,
        title="Critical client deadline review",
        due_date=datetime.utcnow() + timedelta(hours=12),
        estimated_minutes=120,
    )
    db_session.add(task)
    db_session.commit()

    engine = PrioritizationEngine(db_session)
    scored = engine.prioritize_task(task)
    assert scored.urgency_score >= 0.5
    assert scored.importance_score > 0
    assert scored.priority is not None


def test_detect_conflicts(client, demo_user, db_session):
    now = datetime.utcnow() + timedelta(hours=1)

    for title in ["Meeting A", "Meeting B"]:
        db_session.add(
            Event(
                user_id=demo_user.id,
                title=title,
                start_time=now,
                end_time=now + timedelta(hours=1),
            )
        )
    db_session.commit()

    resp = client.get(f"/v1/agent/conflicts?user_id={demo_user.id}")
    assert resp.status_code == 200
    conflicts = resp.json()
    assert len(conflicts) >= 1
