"""Calendar event endpoints."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.security import sanitize_input
from app.db.models import Event
from app.db.session import get_db
from app.schemas import EventCreate, EventResponse

router = APIRouter(prefix="/events", tags=["events"])


@router.get("", response_model=list[EventResponse])
def list_events(
    db: Session = Depends(get_db),
    user_id: int = Query(default=1),
    start: datetime | None = Query(default=None),
    end: datetime | None = Query(default=None),
) -> list[Event]:
    """List calendar events within an optional date range."""
    query = db.query(Event).filter(Event.user_id == user_id)
    if start:
        query = query.filter(Event.start_time >= start)
    if end:
        query = query.filter(Event.end_time <= end)
    return query.order_by(Event.start_time).all()


@router.get("/{event_id}", response_model=EventResponse)
def get_event(event_id: int, db: Session = Depends(get_db)) -> Event:
    """Get a single event."""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.post("", response_model=EventResponse, status_code=201)
def create_event(
    payload: EventCreate,
    db: Session = Depends(get_db),
    user_id: int = Query(default=1),
) -> Event:
    """Create a calendar event."""
    if payload.end_time <= payload.start_time:
        raise HTTPException(status_code=400, detail="end_time must be after start_time")

    event = Event(
        user_id=user_id,
        title=sanitize_input(payload.title, 500),
        description=sanitize_input(payload.description, 5000) if payload.description else None,
        start_time=payload.start_time,
        end_time=payload.end_time,
        location=sanitize_input(payload.location, 500) if payload.location else None,
        attendees=payload.attendees,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event
