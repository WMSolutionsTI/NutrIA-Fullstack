import os
import uuid

from app.db import SessionLocal
from app.domain.models.arquivo import Arquivo
from app.domain.models.arquivo_dispatch import ArquivoDispatch
from app.services.worker_job_service import update_worker_job_status
from app.workers.chatwoot_attachment_worker import enviar_arquivo_chatwoot
from app.workers.minio_worker import download_object
from app.workers.redis_worker import set_if_not_exists


def process_arquivo_dispatch(event: dict):
    event_id = event.get("event_id")
    if event_id and not set_if_not_exists(f"idempotency:{event_id}", "1", expire=3600):
        return

    db = SessionLocal()
    local_path = None
    try:
        payload = event.get("payload", {})
        dispatch_id = payload.get("arquivo_dispatch_id")
        if not dispatch_id:
            if event_id:
                update_worker_job_status(db, event_id=event_id, status="failed", erro="arquivo_dispatch_id_missing")
            return

        dispatch = db.query(ArquivoDispatch).filter(ArquivoDispatch.id == dispatch_id).first()
        if not dispatch:
            if event_id:
                update_worker_job_status(db, event_id=event_id, status="failed", erro="arquivo_dispatch_not_found")
            return

        arquivo = db.query(Arquivo).filter(Arquivo.id == dispatch.arquivo_id).first()
        if not arquivo:
            dispatch.status = "failed"
            dispatch.erro = "arquivo_not_found"
            db.add(dispatch)
            db.commit()
            if event_id:
                update_worker_job_status(db, event_id=event_id, status="failed", erro="arquivo_not_found")
            return

        local_path = f"/tmp/{uuid.uuid4().hex}_{arquivo.nome}"
        if not download_object(arquivo.caminho_s3, local_path):
            dispatch.status = "failed"
            dispatch.erro = "download_failed"
            dispatch.tentativas = int(dispatch.tentativas or 0) + 1
            db.add(dispatch)
            db.commit()
            if event_id:
                update_worker_job_status(
                    db,
                    event_id=event_id,
                    status="failed",
                    tentativas_increment=True,
                    erro="download_failed",
                )
            return

        enviado = enviar_arquivo_chatwoot(dispatch.account_id, dispatch.conversation_id, local_path)
        dispatch.tentativas = int(dispatch.tentativas or 0) + 1
        if enviado:
            dispatch.status = "sent"
            dispatch.erro = None
            if event_id:
                update_worker_job_status(db, event_id=event_id, status="completed")
        else:
            dispatch.status = "failed"
            dispatch.erro = "chatwoot_send_failed"
            if event_id:
                update_worker_job_status(
                    db,
                    event_id=event_id,
                    status="failed",
                    tentativas_increment=True,
                    erro="chatwoot_send_failed",
                )
        db.add(dispatch)
        db.commit()
    except Exception as exc:
        if event_id:
            update_worker_job_status(
                db,
                event_id=event_id,
                status="failed",
                tentativas_increment=True,
                erro=str(exc),
            )
    finally:
        if local_path and os.path.exists(local_path):
            os.remove(local_path)
        db.close()
