from datetime import UTC, datetime, timedelta

from app.db import SessionLocal
from app.domain.models.agenda_evento import AgendaEvento
from app.domain.models.google_calendar_integration import GoogleCalendarIntegration
from app.services.crypto_service import decrypt_text, encrypt_text
from app.services.google_calendar_service import refresh_access_token, token_expiration
from app.services.worker_job_service import update_worker_job_status
from app.workers.redis_worker import set_if_not_exists


def _get_valid_access_token(db, integration: GoogleCalendarIntegration) -> str:
    access_token = decrypt_text(integration.access_token_encrypted)
    expires_at = integration.token_expires_at
    if expires_at and expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=UTC)
    if not expires_at or datetime.now(UTC) < expires_at - timedelta(minutes=1):
        return access_token

    refreshed = refresh_access_token(decrypt_text(integration.refresh_token_encrypted))
    new_access_token = refreshed.get("access_token")
    if not new_access_token:
        raise ValueError("refresh_token_failed")
    integration.access_token_encrypted = encrypt_text(new_access_token)
    integration.refresh_token_encrypted = encrypt_text(
        refreshed.get("refresh_token", decrypt_text(integration.refresh_token_encrypted))
    )
    integration.token_expires_at = token_expiration(refreshed.get("expires_in"))
    integration.atualizado_em = datetime.utcnow()
    db.add(integration)
    db.commit()
    return new_access_token


def process_agenda_sync(event: dict):
    event_id = event.get("event_id")
    if event_id and not set_if_not_exists(f"idempotency:{event_id}", "1", expire=3600):
        return

    db = SessionLocal()
    try:
        payload = event.get("payload", {})
        agenda_evento_id = payload.get("agenda_evento_id")
        if not agenda_evento_id:
            if event_id:
                update_worker_job_status(db, event_id=event_id, status="failed", erro="agenda_evento_id_missing")
            return

        agenda_evento = db.query(AgendaEvento).filter(AgendaEvento.id == agenda_evento_id).first()
        if not agenda_evento:
            if event_id:
                update_worker_job_status(db, event_id=event_id, status="failed", erro="agenda_evento_not_found")
            return

        integration = (
            db.query(GoogleCalendarIntegration)
            .filter(
                GoogleCalendarIntegration.nutricionista_id == agenda_evento.nutricionista_id,
                GoogleCalendarIntegration.status == "active",
            )
            .first()
        )
        if not integration:
            if event_id:
                update_worker_job_status(db, event_id=event_id, status="failed", erro="google_integration_not_active")
            return

        _get_valid_access_token(db, integration)
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
