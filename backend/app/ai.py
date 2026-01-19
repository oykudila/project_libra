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

PLAN_SCHEMA = {
    "name": "plan_todos_v1",
    "schema": {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "assistantText": {"type": "string"},
            "todos": {
                "type": "array",
                "minimumItems": 1,
                "maximumItems": 20,
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "id": {"type": "string"},
                        "title": {"type": "string"},
                        "notes": {"type": "string"},
                        "status": {
                            "type": "string",
                            "enum": ["todo", "in progress", "done"],
                        },
                        "estimate": {"type": "string", "enum": ["S", "M", "L"]},
                        "order": {"type": "integer", "minimum": 1},
                    },
                    "required": [
                        "id",
                        "title",
                        "notes",
                        "status",
                        "estimate",
                        "order",
                    ],
                },
            },
        },
        "required": ["assistantText", "todos"],
    },
    "strict": True,
}


async def generate_todos(goal: str, constraints: dict | None = None) -> dict:
    constraints = constraints or {}

    user_prompt = {
        "goal": goal,
        "constraints": constraints,
        "rules": [
            "Generate 8-15 todos.",
            "Todos must be specific and action-oriented (start with a verb).",
            "Prefer small steps the user can complete in 1-3 hours.",
            "Use simple sequential IDs: t1, t2, t3, ...",
            "Use order starting at 1 and increment by 1 with no gaps.",
            "Set status to 'todo' for all items initially.",
            "Put any assumptions in notes (briefly).",
            "Use S/M/L estimates.",
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
                "content": [
                    {
                        "type": "input_text",
                        "text": json.dumps(user_prompt),
                    }
                ],
            }
        ],
        "text": {
            "format": {
                "type": "json_schema",
                "json_schema": PLAN_SCHEMA,
            }
        },
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        r = await client.post(
            "https://api.openai.com/v1/responses", headers=headers, json=payload
        )

        if r.status_code >= 400:
            print("OpenAI error:", r.status_code, r.text)
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
