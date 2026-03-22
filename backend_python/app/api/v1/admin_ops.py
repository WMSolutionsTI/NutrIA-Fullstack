from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.v1.auth import get_current_user
from app.db import get_db
from app.domain.models.nutricionista import Nutricionista
from app.domain.models.worker_job import WorkerJob
from app.services.event_bus import build_event_payload, publish_event
from app.utils.text_normalize import normalize_pt_text
from app.workers.admin_monitor_worker import coletar_metricas, notificar_admins
from app.workers.rabbitmq_worker import QUEUES, get_queue_depth

router = APIRouter(prefix="/admin/ops", tags=["Admin Ops"])


class AdminOpsCommandRequest(BaseModel):
    comando: str = Field(min_length=3)
    event_id: str | None = None


def _ensure_admin(current_user: Nutricionista) -> None:
    if current_user.papel != "admin":
        raise HTTPException(status_code=403, detail="Acesso negado")


@router.get("/estado", response_model=dict)
def estado_ops(
    db: Session = Depends(get_db),
    current_user: Nutricionista = Depends(get_current_user),
):
    _ensure_admin(current_user)
    grouped = (
        db.query(WorkerJob.status, func.count(WorkerJob.id))
        .group_by(WorkerJob.status)
        .all()
    )
    jobs = {status: count for status, count in grouped}
    queue_depths = {queue: get_queue_depth(queue) for queue in QUEUES}
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "metricas": coletar_metricas(),
        "jobs": jobs,
        "queues": queue_depths,
    }


@router.post("/comando", response_model=dict)
def comando_ops(
    data: AdminOpsCommandRequest,
    db: Session = Depends(get_db),
    current_user: Nutricionista = Depends(get_current_user),
):
    _ensure_admin(current_user)

    comando = normalize_pt_text(data.comando)
    if comando in {"status_filas", "estado_filas", "estado das filas", "status das filas", "filas"}:
        return estado_ops(db, current_user)

    if comando in {"reprocessar_job", "reprocessar", "reprocessar job", "reanalisar job"}:
        if not data.event_id:
            raise HTTPException(status_code=400, detail="event_id é obrigatório para reprocessamento")
        job = db.query(WorkerJob).filter(WorkerJob.event_id == data.event_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job não encontrado")
        event = build_event_payload(
            queue_tipo=f"reprocess_{job.tipo}",
            tenant_id=job.tenant_id,
            nutricionista_id=job.nutricionista_id,
            cliente_id=job.cliente_id,
            payload={"worker_job_id": job.id, "event_id_original": job.event_id},
        )
        publish_event(job.queue, event)
        notificar_admins(f"Reprocessamento solicitado para job {job.event_id} na fila {job.queue}")
        return {"status": "reprocessamento_enfileirado", "event_id": job.event_id}

    raise HTTPException(status_code=400, detail="Comando não suportado")
