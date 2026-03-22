from datetime import datetime
import json

from sqlalchemy.orm import Session

from app.domain.models.worker_job import WorkerJob


def create_worker_job(
    db: Session,
    *,
    event_id: str,
    queue: str,
    tipo: str,
    tenant_id: int,
    nutricionista_id: int,
    cliente_id: int | None,
    payload: dict,
) -> WorkerJob:
    job = WorkerJob(
        event_id=event_id,
        queue=queue,
        tipo=tipo,
        tenant_id=tenant_id,
        nutricionista_id=nutricionista_id,
        cliente_id=cliente_id,
        status="queued",
        tentativas=0,
        payload=json.dumps(payload, ensure_ascii=False),
        criado_em=datetime.utcnow(),
        atualizado_em=datetime.utcnow(),
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def update_worker_job_status(
    db: Session,
    *,
    event_id: str,
    status: str,
    tentativas_increment: bool = False,
    erro: str | None = None,
) -> WorkerJob | None:
    job = db.query(WorkerJob).filter(WorkerJob.event_id == event_id).first()
    if not job:
        return None
    job.status = status
    job.atualizado_em = datetime.utcnow()
    if tentativas_increment:
        job.tentativas = int(job.tentativas or 0) + 1
    if erro:
        job.erro = erro
    db.add(job)
    db.commit()
    db.refresh(job)
    return job
