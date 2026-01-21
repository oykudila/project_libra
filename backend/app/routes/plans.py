from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from .. import models
from ..schemas import (
    PlanGenerateInput,
    PlanApplyInput,
    ProjectDetailResponse,
    PlanResponse,
    PlanReviseInput,
)
from ..ai import generate_plan, revise_plan

router = APIRouter(prefix="/projects/{project_id}/plan", tags=["plans"])
draft_router = APIRouter(prefix="/plan", tags=["plan-draft"])


@router.post("/generate", response_model=PlanResponse)
def generate(
    project_id: int, payload: PlanGenerateInput, db: Session = Depends(get_db)
):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    merge_defaults = payload.model_copy(
        update={
            "goal_text": payload.goal_text or project.goal_text,
            "deadline": payload.deadline or project.deadline,
            "hours_per_week": (
                payload.hours_per_week
                if payload.hours_per_week is not None
                else project.hours_per_week
            ),
        }
    )

    try:
        return generate_plan(merge_defaults)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI planning failed: {e}")


@draft_router.post("/generate", response_model=PlanResponse)
def draft_generate(payload: PlanGenerateInput):
    try:
        return generate_plan(payload)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI planning failed: {e}")


@draft_router.post("/revise", response_model=PlanResponse)
def draft_revise(payload: PlanReviseInput):
    try:
        return revise_plan(payload)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI revise failed: {e}")


@router.post("/revise", response_model=PlanResponse)
def revise(project_id: int, payload: PlanReviseInput, db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    merge_defaults = payload.model_copy(
        update={
            "goal_text": payload.goal_text or project.goal_text,
            "deadline": payload.deadline or project.deadline,
            "hours_per_week": (
                payload.hours_per_week
                if payload.hours_per_week is not None
                else project.hours_per_week
            ),
        }
    )
    try:
        return revise_plan(merge_defaults)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI revise failed: {e}")


@router.post("/apply", response_model=ProjectDetailResponse)
def apply(project_id: int, payload: PlanApplyInput, db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    try:
        db.query(models.Task).filter(models.Task.project_id == project_id).delete()
        db.query(models.Milestone).filter(
            models.Milestone.project_id == project_id
        ).delete()
        db.commit()

        milestones = []
        for m in payload.milestones:
            milestone = models.Milestone(
                project_id=project_id,
                title=m.title,
                description=m.description,
                order_index=m.order_index,
            )
            db.add(milestone)
            milestones.append(milestone)

        db.commit()
        for milestone in milestones:
            db.refresh(milestone)

        # TODO CHECK THIS LOGIC FOR MILESTONE INDEXES
        for t in payload.tasks:
            if t.milestone_index is not None:
                if t.milestone_index < 0 or t.milestone_index >= len(milestones):
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid milestone index {t.milestone_index} for task '{t.title}'.",
                    )
            milestone_id = (
                milestones[t.milestone_index].id
                if t.milestone_index is not None
                else None
            )

            task = models.Task(
                project_id=project_id,
                milestone_id=milestone_id,
                title=t.title,
                description=t.description,
                status=t.status,
                due_date=t.due_date,
                estimate=t.estimate,
                order_index=t.order_index,
            )
            db.add(task)

        db.commit()
        db.refresh(project)
        return project

    except HTTPException:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise
