from __future__ import annotations

import os
import json
import hashlib
from typing import Dict, Optional

from fastapi.encoders import jsonable_encoder
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


def _model_name() -> str:
    return os.getenv("OPENAI_MODEL", "gpt-4.1-mini")


_SYSTEM_PROMPT = (
    "You are a planning assistant. Convert the user's goal into an actionable plan.\n"
    "Return ONLY PlanResponse JSON. No commentary.\n"
    "Constraints:\n"
    "- milestones: exactly 3\n"
    "- If DETAIL=simple: 8 tasks total.\n"
    "- If DETAIL=detailed: 8–12 tasks total.\n"
    "- task.title: short verb phrase; one action\n"
    "- task.description: short how-to instruction\n"
    "- milestone_index: 0|1|2\n"
    "- order_index: 0.. within each milestone\n"
    "- status: todo|in_progress|done (default todo)\n"
    "- estimate: S|M|L (omit if unsure)\n"
    "- No extra fields.\n"
    "Adjust for EXPERIENCE.\n"
)


def _format_common_user_lines(
    payload: PlanGenerateInput | PlanReviseInput,
) -> list[str]:
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

    return lines


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


def _call_plan(model: str, system: str, user: str) -> PlanResponse:
    client = get_openai_client()
    resp = client.responses.parse(
        model=model,
        input=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        max_output_tokens=900,
        temperature=0.2,
        text_format=PlanResponse,
    )
    plan = resp.output_parsed
    if not plan or plan.type != "plan":
        raise RuntimeError("AI did not return a valid plan response.")
    return _normalize_plan(plan)


def _cache_key_generate(p: PlanGenerateInput) -> str:
    parts = [
        p.goal_text.strip(),
        _clean_opt(p.deadline) or "",
        str(p.hours_per_week if p.hours_per_week is not None else ""),
        str(p.experience_level or ""),
        str(p.detail_level or ""),
        _clean_opt(p.constraints) or "",
        _model_name(),
    ]
    raw = "|".join(parts).encode("utf-8", errors="ignore")
    return hashlib.sha256(raw).hexdigest()


def _plan_for_revision_context(plan: PlanResponse) -> dict:
    return {
        "milestones": [{"title": m.title} for m in plan.milestones],
        "tasks": [
            {
                "title": t.title,
                "milestone_index": t.milestone_index,
                "estimate": t.estimate,
            }
            for t in plan.tasks
        ],
    }


def _cache_key_revise(p: PlanReviseInput) -> str:
    model = _model_name()
    current_plan_jsonable = jsonable_encoder(p.current_plan)

    current_hash = hashlib.sha256(
        json.dumps(
            current_plan_jsonable,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8", errors="ignore")
    ).hexdigest()

    parts = [
        p.goal_text.strip(),
        _clean_opt(p.deadline) or "",
        str(p.hours_per_week if p.hours_per_week is not None else ""),
        str(p.experience_level or ""),
        str(p.detail_level or ""),
        _clean_opt(p.constraints) or "",
        current_hash,
        (p.adjustment or "").strip(),
        model,
    ]
    raw = "|".join(parts).encode("utf-8", errors="ignore")
    return hashlib.sha256(raw).hexdigest()


def generate_plan(payload: PlanGenerateInput) -> PlanResponse:
    key = _cache_key_generate(payload)
    cached = _cache.get(key)
    if cached:
        return cached

    model = _model_name()
    user = "\n".join(_format_common_user_lines(payload))

    plan = _call_plan(model=model, system=_SYSTEM_PROMPT, user=user)
    _cache[key] = plan
    return plan


def revise_plan(payload: PlanReviseInput) -> PlanResponse:
    key = _cache_key_revise(payload)
    cached = _revise_cache.get(key)
    if cached:
        return cached

    model = _model_name()

    current = PlanResponse.model_validate(payload.current_plan)
    ctx = jsonable_encoder(_plan_for_revision_context(current))

    user_lines = _format_common_user_lines(payload)
    user = "\n".join(
        [
            *user_lines,
            "CURRENT_PLAN_SUMMARY_JSON:",
            json.dumps(ctx, separators=(",", ":"), ensure_ascii=False),
            "ADJUSTMENT:",
            payload.adjustment.strip(),
        ]
    )

    plan = _call_plan(
        model=model,
        system=_SYSTEM_PROMPT
        + "\nPreserve what still fits; apply the user's adjustment.",
        user=user,
    )
    _revise_cache[key] = plan
    return plan
