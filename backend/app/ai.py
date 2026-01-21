from __future__ import annotations

import os
import json
import hashlib
from typing import Dict, Optional

from openai import OpenAI

from .schemas import PlanGenerateInput, PlanResponse, PlanReviseInput

_client: OpenAI | None = None
_cache: Dict[str, PlanResponse] = {}
_revise_cache: Dict[str, PlanResponse] = {}


def _clean_opt(v: Optional[str]) -> Optional[str]:
    if v is None:
        return None
    s = v.strip()
    return s if s else None


def _cache_key(p: PlanGenerateInput) -> str:
    parts = [
        (p.goal_text or "").strip(),
        str(_clean_opt(p.deadline) or ""),
        str(p.hours_per_week if p.hours_per_week is not None else ""),
        str(p.experience_level or ""),
        str(p.detail_level or ""),
        str(_clean_opt(p.constraints) or ""),
        os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
    ]
    raw = "|".join(parts).encode("utf-8", errors="ignore")
    return hashlib.sha256(raw).hexdigest()


def _normalize_plan(plan: PlanResponse) -> PlanResponse:
    milestone_count = len(plan.milestones)

    for m_i, m in enumerate(plan.milestones):
        if m.order_index is None:
            m.order_index = m_i

    for t in plan.tasks:
        s = (getattr(t, "status", None) or "todo").strip().lower()

        if s in {"doing", "in progress", "in-progress", "inprogress", "wip"}:
            s = "in_progress"
        elif s in {"todo", "to do", "to-do", "backlog", "pending"}:
            s = "todo"
        elif s in {"done", "complete", "completed", "finished"}:
            s = "done"
        else:
            s = "todo"
        t.status = s

        if t.milestone_index is None:
            t.milestone_index = 0
        elif milestone_count > 0 and (
            t.milestone_index < 0 or t.milestone_index >= milestone_count
        ):
            t.milestone_index = 0

        if t.estimate not in (None, "S", "M", "L"):
            t.estimate = None

    return plan


def get_openai_client() -> OpenAI:
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not set in environment variables.")
        _client = OpenAI(api_key=api_key, timeout=20.0)
    return _client


def generate_plan(payload: PlanGenerateInput) -> PlanResponse:
    key = _cache_key(payload)
    if key in _cache:
        return _cache[key]

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

    deadline = _clean_opt(payload.deadline)
    constraints = _clean_opt(payload.constraints)
    exp = payload.experience_level or "beginner"
    detail = payload.detail_level or "simple"

    lines = [
        f"GOAL: {payload.goal_text.strip()}",
        f"EXPERIENCE: {exp}",
        f"DETAIL: {detail}",
    ]
    if deadline:
        lines.append(f"DEADLINE: {deadline}")
    if payload.hours_per_week is not None:
        lines.append(f"HOURS_PER_WEEK: {payload.hours_per_week}")
    if constraints:
        lines.append(f"CONSTRAINTS: {constraints}")

    user = "\n".join(lines)

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
        raise RuntimeError("AI did not return a valid plan response.")

    plan = _normalize_plan(plan)

    _cache[key] = plan
    return plan


def _plan_for_revision_context(plan: PlanResponse) -> dict:
    return {
        "milestones": [
            {"title": m.title, "description": m.description or ""}
            for m in plan.milestones
        ],
        "tasks": [
            {
                "title": t.title,
                "description": t.description or "",
                "milestone_index": t.milestone_index,
                "estimate": t.estimate,
            }
            for t in plan.tasks
        ],
    }


def _revise_cache_key(p: PlanReviseInput) -> str:
    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    current_hash = hashlib.sha256(
        json.dumps(p.current_plan, sort_keys=True, separators=(",", ":")).encode(
            "utf-8", errors="ignore"
        )
    ).hexdigest()

    parts = [
        (p.goal_text or "").strip(),
        str(_clean_opt(p.deadline) or ""),
        str(p.hours_per_week if p.hours_per_week is not None else ""),
        str(p.experience_level or ""),
        str(p.detail_level or ""),
        str(_clean_opt(p.constraints) or ""),
        current_hash,
        (p.adjustment or "").strip(),
        model,
    ]
    raw = "|".join(parts).encode("utf-8", errors="ignore")
    return hashlib.sha256(raw).hexdigest()


def revise_plan(payload: PlanReviseInput) -> PlanResponse:
    key = _revise_cache_key(payload)
    if key in _revise_cache:
        return _revise_cache[key]

    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

    try:
        current = PlanResponse.model_validate(payload.current_plan)
    except Exception as e:
        raise RuntimeError(f"current_plan is not a valid PlanResponse: {e}")

    system = (
        "Return ONLY PlanResponse JSON.\n"
        "Rules: exactly 3 milestones; 8-12 tasks; each task is one action; "
        "milestone_index in 0,1,2; order_index starts at 0 per milestone; "
        "status in todo|in_progress|done; estimate S|M|L or omit; "
        "no extra fields; no commentary."
    )

    deadline = _clean_opt(payload.deadline)
    constraints = _clean_opt(payload.constraints)
    exp = payload.experience_level or "beginner"
    detail = payload.detail_level or "simple"

    # send a compact plan context instead of full dump
    ctx = _plan_for_revision_context(current)

    user = "\n".join(
        [
            f"GOAL: {payload.goal_text.strip()}",
            f"EXPERIENCE: {exp}",
            f"DETAIL: {detail}",
            *([f"DEADLINE: {deadline}"] if deadline else []),
            *(
                [f"HOURS_PER_WEEK: {payload.hours_per_week}"]
                if payload.hours_per_week is not None
                else []
            ),
            *([f"CONSTRAINTS: {constraints}"] if constraints else []),
            "CURRENT_PLAN_SUMMARY_JSON:",
            json.dumps(ctx, separators=(",", ":"), ensure_ascii=False),
            "ADJUSTMENT:",
            payload.adjustment.strip(),
        ]
    )

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
        raise RuntimeError("AI did not return a valid plan response.")

    plan = _normalize_plan(plan)
    _revise_cache[key] = plan
    return plan
