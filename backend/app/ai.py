import os, json
import httpx
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("AI_MODEL", "gpt-4.1-mini")

if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY is missing from backend/.env.")

SYSTEM = (
    "You are an AI assistant that helps users tackle complex goals by breaking them into actionable steps."
    "You generate task lists that are consumed directly by a user interface."
    "You MUST return ONLY valid JSON that matches the requested schema."
    "Do not include Markdown, comments, or any extra text outside the JSON."
)


async def generate_todos(goal: str, constraints: dict | None = None) -> dict:
    """Generate a list of todos to achieve a goal using OpenAI's API."""
    constraints = constraints or {}

    prompt = {
        "goal": goal,
        "constraints": constraints,
        "output_format": {
            "assistantText": "string",
            "todos": [
                {
                    "id": "t1",
                    "title": "string",
                    "notes": "string",
                    "status": "todo",
                    "estimate": "S|M|L",
                    "order": 1,
                }
            ],
        },
        "rules": [
            "Generate 8-15 todos.",
            "Todos must be actionable and concrete.",
            "Use status 'todo' for all items.",
            "Use S/M/L estimates.",
            "Order must start at 1 and increment by 1.",
        ],
    }

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": OPENAI_MODEL,
        "instructions": SYSTEM,
        "input": [
            {
                "role": "user",
                "content": [{"type": "input_text", "text": json.dumps(prompt)}],
            }
        ],
        "text": {"format": {"type": "json_object"}},
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        r = await client.post(
            "https://api.openai.com/v1/responses", headers=headers, json=payload
        )
        r.raise_for_status()
        data = r.json()

    out_text = None
    for item in data.get("output", []):
        for c in item.get("content", []):
            if c.get("type") in ("output_text", "text"):
                out_text = c.get("text")
                break
        if out_text:
            break

    if not out_text:
        raise RuntimeError("No output text found.")

    return json.loads(out_text)
