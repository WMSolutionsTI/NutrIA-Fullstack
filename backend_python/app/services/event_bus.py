from datetime import UTC, datetime
import json
import uuid

from app.workers.rabbitmq_worker import send_message


def build_event_payload(
    *,
    queue_tipo: str,
    tenant_id: int,
    nutricionista_id: int,
    payload: dict,
    cliente_id: int | None = None,
    event_id: str | None = None,
) -> dict:
    return {
        "event_id": event_id or uuid.uuid4().hex,
        "tenant_id": tenant_id,
        "nutricionista_id": nutricionista_id,
        "cliente_id": cliente_id,
        "tipo": queue_tipo,
        "payload": payload,
        "created_at": datetime.now(UTC).isoformat(),
    }


def publish_event(queue: str, event: dict) -> bool:
    return send_message(queue, json.dumps(event, ensure_ascii=False))
