"""Task prioritization engine — Eisenhower Matrix + ML scoring."""

import logging
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.db.models import Task, TaskPriority, TaskStatus
from app.services.cache import cache_service

logger = logging.getLogger(__name__)

CACHE_TTL = 300


class PrioritizationEngine:
    """Scores and ranks tasks using urgency/importance heuristics."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def compute_urgency(self, task: Task, now: datetime | None = None) -> float:
        """Higher score = more urgent (0-1)."""
        now = now or datetime.utcnow()
        if not task.due_date:
            return 0.3

        hours_until_due = (task.due_date - now).total_seconds() / 3600
        if hours_until_due <= 0:
            return 1.0
        if hours_until_due <= 24:
            return 0.9
        if hours_until_due <= 72:
            return 0.7
        if hours_until_due <= 168:
            return 0.5
        return 0.2

    def compute_importance(self, task: Task) -> float:
        """Heuristic importance based on keywords and estimated effort."""
        high_importance_keywords = [
            "deadline",
            "client",
            "release",
            "review",
            "presentation",
            "blocker",
            "critical",
        ]
        text = f"{task.title} {task.description or ''}".lower()
        keyword_hits = sum(1 for kw in high_importance_keywords if kw in text)
        base = min(0.3 + keyword_hits * 0.15, 0.9)

        if task.estimated_minutes >= 120:
            base = min(base + 0.1, 1.0)
        return base

    def compute_ml_score(self, urgency: float, importance: float) -> float:
        """Weighted composite score (placeholder for future ML model)."""
        return round(0.55 * urgency + 0.45 * importance, 4)

    def classify_eisenhower(self, urgency: float, importance: float) -> TaskPriority:
        """Map scores to Eisenhower quadrant."""
        urgent = urgency >= 0.5
        important = importance >= 0.5
        if urgent and important:
            return TaskPriority.URGENT_IMPORTANT
        if not urgent and important:
            return TaskPriority.NOT_URGENT_IMPORTANT
        if urgent and not important:
            return TaskPriority.URGENT_NOT_IMPORTANT
        return TaskPriority.NOT_URGENT_NOT_IMPORTANT

    def prioritize_task(self, task: Task) -> Task:
        """Score a single task and persist."""
        cache_key = f"task_score:{task.id}"
        cached = cache_service.get(cache_key)
        if cached:
            task.urgency_score = cached["urgency"]
            task.importance_score = cached["importance"]
            task.ml_score = cached["ml_score"]
            task.priority = TaskPriority(cached["priority"])
            return task

        urgency = self.compute_urgency(task)
        importance = self.compute_importance(task)
        ml_score = self.compute_ml_score(urgency, importance)
        priority = self.classify_eisenhower(urgency, importance)

        task.urgency_score = urgency
        task.importance_score = importance
        task.ml_score = ml_score
        task.priority = priority

        cache_service.set(
            cache_key,
            {
                "urgency": urgency,
                "importance": importance,
                "ml_score": ml_score,
                "priority": priority.value,
            },
            CACHE_TTL,
        )
        return task

    def prioritize_all(self, user_id: int) -> list[Task]:
        """Re-score all open tasks for a user, sorted by ML score descending."""
        tasks = (
            self.db.query(Task)
            .filter(Task.user_id == user_id, Task.status != TaskStatus.DONE)
            .all()
        )
        for task in tasks:
            self.prioritize_task(task)
        self.db.commit()
        tasks.sort(key=lambda t: t.ml_score, reverse=True)
        logger.info("Prioritized %d tasks for user %d", len(tasks), user_id)
        return tasks
