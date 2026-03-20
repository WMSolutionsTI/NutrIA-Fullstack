from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db import init_db
from app.api.v1 import router as api_router

app = FastAPI(title="NutrIA API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://nutriapro.com.br",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    init_db()

app.include_router(api_router, prefix="/api/v1")

