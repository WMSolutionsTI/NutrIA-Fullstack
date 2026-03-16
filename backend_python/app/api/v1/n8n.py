from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db

router = APIRouter()

@router.post("/n8n/trigger")
def trigger_n8n_workflow(workflow_id: str, payload: dict):
    # Mock: disparo de workflow n8n via API
    # Aqui seria feita a chamada HTTP para n8n
    return {"workflow_id": workflow_id, "status": "triggered", "payload": payload}

@router.get("/n8n/workflow/{workflow_id}/status")
def status_n8n_workflow(workflow_id: str):
    # Mock: consulta status workflow n8n
    return {"workflow_id": workflow_id, "status": "completed"}

@router.get("/n8n/workflow/{workflow_id}/logs")
def logs_n8n_workflow(workflow_id: str):
    # Mock: logs de workflow n8n
    return {"workflow_id": workflow_id, "logs": ["step1 ok", "step2 ok"]}