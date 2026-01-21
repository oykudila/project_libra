from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models
from ..database import get_db
from ..schemas import TaskResponse, TaskUpdate, TaskCreate

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", response_model=TaskResponse)
def create_task(payload: TaskCreate, db: Session = Depends(get_db)):
    project = (
        db.query(models.Project).filter(models.Project.id == payload.project_id).first()
    )
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    title = (payload.title or "").strip()
    if not title:
        raise HTTPException(status_code=400, detail="Title is required")

    insert_at = 0 if payload.order_index is None else payload.order_index
    if insert_at < 0:
        insert_at = 0

    db.query(models.Task).filter(
        models.Task.project_id == payload.project_id,
        models.Task.status == payload.status,
        models.Task.order_index >= insert_at,
    ).update({models.Task.order_index: models.Task.order_index + 1})

    task = models.Task(
        project_id=payload.project_id,
        milestone_id=payload.milestone_id,
        title=title,
        description=payload.description,
        status=payload.status,
        due_date=payload.due_date,
        estimate=payload.estimate,
        order_index=insert_at,
    )

    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.patch("/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, payload: TaskUpdate, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    data = payload.model_dump(exclude_unset=True)
    if not data:
        raise HTTPException(status_code=400, detail="Nothing updated")
    for field, value in data.items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(task)
    db.commit()
    return {"ok": True}
