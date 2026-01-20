from pathlib import Path
from dotenv import load_dotenv

ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=ENV_PATH)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from . import models
from .database import Base, engine
from .routes import projects, plans, tasks


from openai import OpenAI
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    def health():
        return {"status": "ok"}

    app.include_router(projects.router)
    app.include_router(plans.router)
    app.include_router(tasks.router)

    return app


app = create_app()


@app.get("/debug/openai-models")
def debug_openai_models():
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    models = client.models.list()
    # return just IDs (safe)
    return {"models": [m.id for m in models.data]}
