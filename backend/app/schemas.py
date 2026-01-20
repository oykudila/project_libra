from pydantic import BaseModel
from typing import Optional, List, Literal

TaskStatus = Literal["todo", "in_progress", "done"]
TaskSize = Literal["S", "M", "L"]


class ProjectCreate(BaseModel):
    title: str
    goal_text: str
    deadline: Optional[str] = None
    hours_per_week: Optional[int] = None


class ProjectResponse(BaseModel):
    id: int
    title: str
    goal_text: str
    deadline: Optional[str] = None
    hours_per_week: Optional[int] = None

    class Config:
        from_attributes = True


class MilestoneResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    order_index: int

    class Config:
        from_attributes = True


class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    status: TaskStatus
    due_date: Optional[str] = None
    estimate: Optional[TaskSize] = None
    order_index: int
    milestone_id: Optional[int] = None

    class Config:
        from_attributes = True


class ProjectDetailResponse(ProjectResponse):
    milestones: List[MilestoneResponse]
    tasks: List[TaskResponse]


# AI


class PlanGenerateInput(BaseModel):
    goal_text: str
    deadline: Optional[str] = None
    hours_per_week: Optional[int] = None
    experience_level: Optional[Literal["beginner", "intermediate", "advanced"]] = None
    detail_level: Optional[Literal["simple", "detailed"]] = "simple"
    constraints: Optional[str] = None


class ProposeMilestone(BaseModel):
    title: str
    description: Optional[str] = None
    order_index: int = 0


class ProposeTask(BaseModel):
    title: str
    description: Optional[str] = None
    milestone_index: Optional[int] = None
    status: TaskStatus = "todo"
    due_date: Optional[str] = None
    estimate: Optional[TaskSize] = None
    order_index: int = 0


class PlanApplyInput(BaseModel):
    milestones: List[ProposeMilestone]
    tasks: List[ProposeTask]


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    due_date: Optional[str] = None
    estimate: Optional[TaskSize] = None
    order_index: Optional[int] = None
    milestone_id: Optional[int] = None


class PlanResponse(BaseModel):
    type: Literal["plan"]
    milestones: List[ProposeMilestone]
    tasks: List[ProposeTask]
