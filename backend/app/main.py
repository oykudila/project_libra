from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import plans


app = FastAPI(title="Todos Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"ok": True}


app.include_router(plans.router, prefix="/plans")
