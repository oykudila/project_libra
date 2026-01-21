from __future__ import annotations

from typing import Annotated, List, Literal, Optional

from pydantic import BaseModel, Field, ConfigDict


TaskStatus = Literal["todo", "in_progress", "done"]
TaskSize = Literal["S", "M", "L"]
ExperienceLevel = Literal["beginner", "intermediate", "advanced"]
DetailLevel = Literal["simple", "detailed"]

NonEmptyStr = Annotated[str, Field(min_length=1)]
NonNegInt = Annotated[int, Field(ge=0)]


# --- Projects ---
class ProjectCreate(BaseModel):
    title: NonEmptyStr
    goal_text: NonEmptyStr
    deadline: Optional[str] = None
    hours_per_week: Optional[NonNegInt] = None


class ProjectResponse(BaseModel):
    id: int
    title: str
    goal_text: str
    deadline: Optional[str] = None
    hours_per_week: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class MilestoneResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    order_index: int

    model_config = ConfigDict(from_attributes=True)


class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    status: TaskStatus
    due_date: Optional[str] = None
    estimate: Optional[TaskSize] = None
    order_index: int
    milestone_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class ProjectDetailResponse(ProjectResponse):
    milestones: List[MilestoneResponse] = Field(default_factory=list)
    tasks: List[TaskResponse] = Field(default_factory=list)


class TaskUpdate(BaseModel):
    title: Optional[NonEmptyStr] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    due_date: Optional[str] = None
    estimate: Optional[TaskSize] = None
    order_index: Optional[NonNegInt] = None
    milestone_id: Optional[int] = None


class TaskCreate(BaseModel):
    project_id: int
    title: NonEmptyStr
    description: Optional[str] = None
    status: TaskStatus = "todo"
    due_date: Optional[str] = None
    estimate: Optional[TaskSize] = None
    order_index: Optional[NonNegInt] = None
    milestone_id: Optional[int] = None


# --- AI generations ---
class ProposeMilestone(BaseModel):
    title: NonEmptyStr
    description: Optional[str] = None
    order_index: NonNegInt = 0


class ProposeTask(BaseModel):
    title: NonEmptyStr
    description: Optional[str] = None
    milestone_index: Optional[int] = None
    status: TaskStatus = "todo"
    due_date: Optional[str] = None
    estimate: Optional[TaskSize] = None
    order_index: NonNegInt = 0


class PlanResponse(BaseModel):
    type: Literal["plan"]
    milestones: List[ProposeMilestone] = Field(default_factory=list)
    tasks: List[ProposeTask] = Field(default_factory=list)


class PlanGenerateInput(BaseModel):
    goal_text: NonEmptyStr
    deadline: Optional[str] = None
    hours_per_week: Optional[NonNegInt] = None
    experience_level: Optional[ExperienceLevel] = None
    detail_level: Optional[DetailLevel] = "simple"
    constraints: Optional[str] = None


class PlanApplyInput(BaseModel):
    milestones: List[ProposeMilestone] = Field(default_factory=list)
    tasks: List[ProposeTask] = Field(default_factory=list)


class PlanReviseInput(BaseModel):
    goal_text: NonEmptyStr
    deadline: Optional[str] = None
    hours_per_week: Optional[NonNegInt] = None
    experience_level: Optional[ExperienceLevel] = None
    detail_level: Optional[DetailLevel] = "simple"
    constraints: Optional[str] = None
    current_plan: PlanResponse
    adjustment: NonEmptyStr
