from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from app.db import init_db
from app.api.v1 import router as api_router

app = FastAPI(title="NutrIA API")


def _origens_permitidas() -> list[str]:
    custom = os.getenv("CORS_ALLOWED_ORIGINS", "").strip()
    if custom:
        return [item.strip() for item in custom.split(",") if item.strip()]
    return [
        "https://nutriapro.com.br",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "http://localhost:3002",
        "http://127.0.0.1:3002",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origens_permitidas(),
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    if os.getenv("TEST_ENV", "0") == "1" or os.getenv("SKIP_STARTUP_DB_INIT", "0") == "1":
        return
    init_db()

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(api_router, prefix="/api/v1")
