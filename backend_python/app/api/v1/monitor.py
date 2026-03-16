from fastapi import APIRouter
import os

router = APIRouter()

@router.get("/monitor/health")
def health_check():
    return {"status": "ok", "hostname": os.uname().nodename}

@router.get("/monitor/metrics")
def metrics():
    # Mock: métricas básicas
    return {"cpu": "normal", "memory": "normal", "workers": 3}