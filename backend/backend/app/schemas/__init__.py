"""Pydantic schemas for API request/response validation."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class TaskPriority(str, Enum):
    URGENT_IMPORTANT = "urgent_important"
    NOT_URGENT_IMPORTANT = "not_urgent_important"
    URGENT_NOT_IMPORTANT = "urgent_not_important"
    NOT_URGENT_NOT_IMPORTANT = "not_urgent_not_important"


class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    BLOCKED = "blocked"


class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    description: str | None = None
    status: TaskStatus = TaskStatus.TODO
    due_date: datetime | None = None
    estimated_minutes: int = Field(default=30, ge=1, le=480)


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=500)
    description: str | None = None
    status: TaskStatus | None = None
    due_date: datetime | None = None
    estimated_minutes: int | None = Field(None, ge=1, le=480)


class TaskResponse(TaskBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    priority: TaskPriority | None = None
    urgency_score: float = 0.0
    importance_score: float = 0.0
    ml_score: float = 0.0
    source: str = "synthetic"
    created_at: datetime
    updated_at: datetime


class EventBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    description: str | None = None
    start_time: datetime
    end_time: datetime
    location: str | None = None


class EventCreate(EventBase):
    attendees: str | None = None


class EventResponse(EventBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    has_conflict: bool = False
    meeting_notes: str | None = None
    created_at: datetime


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)


class ChatResponse(BaseModel):
    reply: str
    confidence: float
    actions_taken: list[str] = []
    action_cards: list[dict] = []


class AgentMetricsResponse(BaseModel):
    conflicts_resolved: int = 0
    deadlines_rescued: int = 0
    meetings_prepped: int = 0
    focus_score: int = 85
    streak_days: int = 0


class HealthResponse(BaseModel):
    status: str
    version: str
    database: str
    redis: str
