from app.db import SessionLocal
from app.services.worker_job_service import update_worker_job_status
from app.workers.admin_monitor_worker import notificar_admins, status_do_sistema
from app.workers.redis_worker import set_if_not_exists


def process_admin_ops(event: dict):
    event_id = event.get("event_id")
    if event_id and not set_if_not_exists(f"idempotency:{event_id}", "1", expire=3600):
        return

    db = SessionLocal()
    try:
        payload = event.get("payload", {})
        comando = str(payload.get("comando", "")).lower()
        if comando == "snapshot":
            notificar_admins(status_do_sistema())
        else:
            notificar_admins(f"[admin-ops] comando recebido: {comando or 'desconhecido'}")
        if event_id:
            update_worker_job_status(db, event_id=event_id, status="completed")
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
        db.close()
