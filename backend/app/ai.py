from typing import Union
from .schemas import (
    PlanGenerateInput,
    PlanQuestionsResponse,
    PlanResponse,
    PlanQuestion,
    ProposeMilestone,
    ProposeTask,
)


def generate_plan_or_questions(
    payload: PlanGenerateInput,
) -> Union[PlanQuestionsResponse, PlanResponse]:
    missing = []

    if not payload.deadline:
        missing.append(("deadline", "What is your target deadline?"))
    if payload.hours_per_week is None:
        missing.append(
            (
                "hours_per_week",
                "How many hours per week do you want to spend on this?",
            )
        )
    if not payload.experience_level:
        missing.append(("experience_level", "What is your experience level?"))

    if missing:
        return PlanQuestionsResponse(
            type="questions",
            questions=[
                PlanQuestion(id=f"q{i+1}", field=f, question=q)
                for i, (f, q) in enumerate(missing)
            ],
        )

    milestones = [
        ProposeMilestone(
            title="Define success and constraints",
            description="Clarify what done means.",
            order_index=0,
        ),
        ProposeMilestone(
            title="Build the core plan",
            description="Break down into milestones and tasks.",
            order_index=1,
        ),
        ProposeMilestone(
            title="Review weekly", description="Work weekly and adjust.", order_index=2
        ),
    ]
    tasks = [
        ProposeTask(
            title="Write your definition of success",
            milestone_index=0,
            estimate="S",
            order_index=0,
        ),
        ProposeTask(
            title="List any constraints", milestone_index=0, estimate="S", order_index=1
        ),
        ProposeTask(
            title="Draft 3 to 5 milestones for the goal",
            milestone_index=1,
            estimate="L",
            order_index=0,
        ),
        ProposeTask(
            title="Pick top 3 tasks for this week",
            milestone_index=2,
            estimate="M",
            order_index=0,
        ),
        ProposeTask(
            title="At the end of the week, review progress",
            milestone_index=2,
            estimate="M",
            order_index=1,
        ),
    ]

    return PlanResponse(type="plan", milestones=milestones, tasks=tasks)
