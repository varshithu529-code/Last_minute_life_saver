"""Task CRUD and prioritization endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from app.core.rate_limit import limiter
from app.core.security import sanitize_input
from app.db.models import Task
from app.db.session import get_db
from app.schemas import TaskCreate, TaskResponse, TaskUpdate
from app.services.prioritization import PrioritizationEngine

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("", response_model=list[TaskResponse])
def list_tasks(
    db: Session = Depends(get_db),
    user_id: int = Query(default=1),
    prioritize: bool = Query(default=False),
) -> list[Task]:
    """List tasks, optionally re-prioritized."""
    if prioritize:
        engine = PrioritizationEngine(db)
        return engine.prioritize_all(user_id)

    return db.query(Task).filter(Task.user_id == user_id).order_by(Task.due_date).all()


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)) -> Task:
    """Get a single task."""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.post("", response_model=TaskResponse, status_code=201)
@limiter.limit("30/minute")
def create_task(
    request: Request,
    payload: TaskCreate,
    db: Session = Depends(get_db),
    user_id: int = Query(default=1),
) -> Task:
    """Create a new task."""
    task = Task(
        user_id=user_id,
        title=sanitize_input(payload.title, 500),
        description=sanitize_input(payload.description, 5000) if payload.description else None,
        status=payload.status,
        due_date=payload.due_date,
        estimated_minutes=payload.estimated_minutes,
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    engine = PrioritizationEngine(db)
    engine.prioritize_task(task)
    db.commit()
    db.refresh(task)
    return task


@router.patch("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    payload: TaskUpdate,
    db: Session = Depends(get_db),
) -> Task:
    """Update an existing task."""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    update_data = payload.model_dump(exclude_unset=True)
    if "title" in update_data and update_data["title"]:
        update_data["title"] = sanitize_input(update_data["title"], 500)
    if "description" in update_data and update_data["description"]:
        update_data["description"] = sanitize_input(update_data["description"], 5000)

    for key, value in update_data.items():
        setattr(task, key, value)

    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: int, db: Session = Depends(get_db)) -> None:
    """Delete a task."""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
