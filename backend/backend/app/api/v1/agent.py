"""Autonomous agent and chat endpoints."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.security import sanitize_input
from app.db.models import AgentLog
from app.db.session import get_db
from app.schemas import AgentMetricsResponse, ChatRequest, ChatResponse
from app.services.agent import AutonomousAgent
from app.services.agent.cards import build_action_cards

router = APIRouter(tags=["agent"])


@router.get("/agent/metrics", response_model=AgentMetricsResponse)
def get_agent_metrics(
    db: Session = Depends(get_db),
    user_id: int = Query(default=1),
) -> AgentMetricsResponse:
    """Dashboard snapshot: impact metrics + gamification."""
    return AutonomousAgent(db, user_id=user_id).get_metrics()


@router.post("/agent/run", response_model=dict)
def run_agent_workflow(
    db: Session = Depends(get_db),
    user_id: int = Query(default=1),
) -> dict:
    """Run the LangGraph demo workflow: conflicts, reschedule, deadlines, prep."""
    agent = AutonomousAgent(db, user_id=user_id)
    result = agent.run_workflow_demo()
    result["action_cards"] = build_action_cards(result)
    return result


@router.get("/agent/conflicts", response_model=list[dict])
def detect_conflicts(
    db: Session = Depends(get_db),
    user_id: int = Query(default=1),
) -> list[dict]:
    """Detect calendar conflicts."""
    return AutonomousAgent(db, user_id=user_id).detect_conflicts()


@router.post("/agent/reschedule/{event_id}", response_model=dict)
def propose_reschedule(
    event_id: int,
    db: Session = Depends(get_db),
    user_id: int = Query(default=1),
) -> dict:
    """Propose a reschedule for a conflicting event."""
    return AutonomousAgent(db, user_id=user_id).propose_reschedule(event_id)


@router.post("/agent/reschedule/{event_id}/execute", response_model=dict)
def execute_reschedule(
    event_id: int,
    new_start: datetime,
    db: Session = Depends(get_db),
    user_id: int = Query(default=1),
) -> dict:
    """Execute a reschedule via calendar provider."""
    return AutonomousAgent(db, user_id=user_id).execute_reschedule(event_id, new_start)


@router.get("/agent/deadline-rescue", response_model=list[dict])
def deadline_rescue(
    db: Session = Depends(get_db),
    user_id: int = Query(default=1),
) -> list[dict]:
    """Find urgent deadlines and draft extension emails."""
    return AutonomousAgent(db, user_id=user_id).deadline_rescue()


@router.get("/agent/meeting-prep/{event_id}", response_model=dict)
def meeting_prep(
    event_id: int,
    db: Session = Depends(get_db),
    user_id: int = Query(default=1),
) -> dict:
    """Generate meeting prep checklist."""
    result = AutonomousAgent(db, user_id=user_id).meeting_prep(event_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.get("/agent/logs", response_model=list[dict])
def list_agent_logs(
    db: Session = Depends(get_db),
    user_id: int = Query(default=1),
    limit: int = Query(default=50, le=200),
) -> list[dict]:
    """Dashboard: all autonomous agent actions."""
    logs = (
        db.query(AgentLog)
        .filter(AgentLog.user_id == user_id)
        .order_by(AgentLog.created_at.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "id": log.id,
            "action_type": log.action_type,
            "description": log.description,
            "confidence": log.confidence,
            "status": log.status,
            "created_at": log.created_at.isoformat(),
        }
        for log in logs
    ]


@router.post("/chat", response_model=ChatResponse)
def chat_endpoint(
    payload: ChatRequest,
    db: Session = Depends(get_db),
    user_id: int = Query(default=1),
) -> ChatResponse:
    """Chat interface backed by LangChain LLM with agent context."""
    message = sanitize_input(payload.message, 2000)
    result = AutonomousAgent(db, user_id=user_id).handle_intent(message)
    return ChatResponse(
        reply=result["reply"],
        confidence=result["confidence"],
        actions_taken=result.get("actions_taken", []),
        action_cards=result.get("action_cards", []),
    )
