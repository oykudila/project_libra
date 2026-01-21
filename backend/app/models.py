from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from .database import Base

TASK_STATUSES = ("todo", "in_progress", "done")
TASK_SIZES = ("S", "M", "L")


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    goal_text = Column(Text, nullable=False)
    deadline = Column(String, nullable=True)
    hours_per_week = Column(Integer, nullable=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    milestones = relationship(
        "Milestone",
        back_populates="project",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="Milestone.order_index",
    )
    tasks = relationship(
        "Task",
        back_populates="project",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="Task.order_index",
    )


class Milestone(Base):
    __tablename__ = "milestones"

    id = Column(Integer, primary_key=True)
    project_id = Column(
        Integer,
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    order_index = Column(Integer, nullable=False, default=0)

    project = relationship("Project", back_populates="milestones")
    tasks = relationship(
        "Task",
        back_populates="milestone",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="Task.order_index",
    )


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True)
    project_id = Column(
        Integer,
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    milestone_id = Column(
        Integer,
        ForeignKey("milestones.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String, nullable=False, default="todo")  # todo, in_progress, done
    due_date = Column(String, nullable=True)
    estimate = Column(String, nullable=True)  # S, M, L
    order_index = Column(Integer, nullable=False, default=0)

    project = relationship("Project", back_populates="tasks")
    milestone = relationship("Milestone", back_populates="tasks")
