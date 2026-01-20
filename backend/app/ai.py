from __future__ import annotations

import os
import hashlib
from typing import Dict, Optional

from openai import OpenAI

from .schemas import (
    PlanGenerateInput,
    PlanResponse,
)

_client: OpenAI | None = None
_cache: Dict[str, PlanResponse] = {}


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


def get_openai_client() -> OpenAI:
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not set in environment variables.")
        _client = OpenAI(api_key=api_key, timeout=30.0)
    return _client


def generate_plan(
    payload: PlanGenerateInput,
) -> PlanResponse:
    key = _cache_key(payload)
    if key in _cache:
        return _cache[key]

    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

    system = (
        "Return a SHORT plan in PlanResponse JSON only.\n"
        "Constraints:\n"
        "- Exactly 3 milestones.\n"
        "- 8–12 tasks total.\n"
        "- Each task is one action.\n"
        "- milestone_index must be 0,1,2.\n"
        "- order_index starts at 0 within each milestone.\n"
        "- status must be todo, in_progress, or done (default todo).\n"
        "- estimate must be S, M, or L (omit if unsure).\n"
        "- No extra fields. No commentary.\n"
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

    _cache[key] = plan
    return plan
