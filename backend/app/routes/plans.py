from fastapi import APIRouter
from pydantic import BaseModel
from typing import Any, Dict, Optional
from app.ai import generate_todos

router = APIRouter()


class GenerateBody(BaseModel):
    goal: str
    constraints: Optional[Dict[str, Any]] = None


@router.post("/generate")
async def generate(body: GenerateBody):
    result = await generate_todos(body.goal, body.constraints)
    return result
