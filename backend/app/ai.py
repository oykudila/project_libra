from __future__ import annotations

import os
from typing import Union
from openai import OpenAI

from .schemas import (
    PlanGenerateInput,
    PlanQuestionsResponse,
    PlanResponse,
    PlanQuestion,
    ProposeMilestone,
    ProposeTask,
)

_client: OpenAI | None = None


def get_openai_client() -> OpenAI:
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not set in environment variables.")
        _client = OpenAI(api_key=api_key)
    return _client


def _fallback_plan() -> PlanResponse:
    milestones = [
        ProposeMilestone(
            title="Define success and constraints",
            description="Clarify what done means and what limits you have.",
            order_index=0,
        ),
        ProposeMilestone(
            title="Build the core plan",
            description="Break the goal into milestones and tasks.",
            order_index=1,
        ),
        ProposeMilestone(
            title="Execute and review weekly",
            description="Pick weekly priorities and adjust based on progress.",
            order_index=2,
        ),
    ]
    tasks = [
        ProposeTask(
            title="Write a definition of success",
            milestone_index=0,
            estimate="S",
            order_index=0,
        ),
        ProposeTask(
            title="List constraints and risks",
            milestone_index=0,
            estimate="S",
            order_index=1,
        ),
        ProposeTask(
            title="Draft 3–5 milestones", milestone_index=1, estimate="M", order_index=0
        ),
        ProposeTask(
            title="Pick top 3 tasks for this week",
            milestone_index=2,
            estimate="M",
            order_index=0,
        ),
        ProposeTask(
            title="End-of-week review + adjust plan",
            milestone_index=2,
            estimate="S",
            order_index=1,
        ),
    ]
    return PlanResponse(type="plan", milestones=milestones, tasks=tasks)


def generate_plan_or_questions(
    payload: PlanGenerateInput,
) -> Union[PlanQuestionsResponse, PlanResponse]:
    missing = []

    if not payload.deadline:
        missing.append(("deadline", "What is your target deadline?"))
    if payload.hours_per_week is None:
        missing.append(
            ("hours_per_week", "How many hours per week do you want to spend on this?")
        )
    if not payload.experience_level:
        missing.append(
            (
                "experience_level",
                "What is your experience level? (beginner/intermediate/advanced)",
            )
        )

    if missing:
        return PlanQuestionsResponse(
            type="questions",
            questions=[
                PlanQuestion(id=f"q{i+1}", field=f, question=q)
                for i, (f, q) in enumerate(missing)
            ],
        )

    # Deterministic plan as a fallback if no OpenAI key is available
    if not os.getenv("OPENAI_API_KEY"):
        return _fallback_plan()

    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

    system = (
        "You are a planning assistant. Convert the user's goal into an actionable plan.\n"
        "Return milestones and tasks that are realistic for the provided time budget and deadline.\n"
        "Rules:\n"
        "- milestone_index must refer to the index of the milestones list (0..n-1)\n"
        "- order_index starts at 0 within milestones and within each milestone's tasks\n"
        "- estimates must be one of: S, M, L\n"
        "- statuses must be one of: todo, doing, done (use todo by default)\n"
        "- Keep tasks specific, testable, and phrased as actions.\n"
    )

    detail_hint = (
        "Keep it concise: 3 milestones, ~8-12 tasks total."
        if payload.detail_level == "simple"
        else "Be thorough: 4-6 milestones, ~15-30 tasks total."
    )

    user = (
        f"GOAL:\n{payload.goal_text}\n\n"
        f"DEADLINE:\n{payload.deadline}\n\n"
        f"HOURS PER WEEK:\n{payload.hours_per_week}\n\n"
        f"EXPERIENCE LEVEL:\n{payload.experience_level}\n\n"
        f"DETAIL:\n{payload.detail_level} ({detail_hint})\n\n"
        f"CONSTRAINTS (optional):\n{payload.constraints or 'None'}\n"
    )

    try:
        print("DEBUG: OPENAI_API_KEY present:", bool(os.getenv("OPENAI_API_KEY")))
        print("DEBUG: Using model:", model)

        client = get_openai_client()
        resp = client.responses.parse(
            model=model,
            input=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            text_format=PlanResponse,
        )
        plan = resp.output_parsed

        if not plan or plan.type != "plan":
            return _fallback_plan()

        for t in plan.tasks:
            if t.milestone_index is None:
                t.milestone_index = 0
            if not t.status:
                t.status = "todo"

        return plan

    except Exception as e:
        print("DEBUG: Exception occurred:", e)
        return _fallback_plan()
