import json
import os

import pika

from app.workers.arquivo_dispatch_worker import process_arquivo_dispatch
from app.workers.atendimento_workflow_worker import process_atendimento_workflow
from app.workers.meal_support_worker import process_notification_event
from app.workers.quebrar_enviar_mensagens_worker import enviar_mensagens
from app.workers.specialist_task_worker import process_specialist_task
from app.workers.worker_admin_ops import process_admin_ops
from app.workers.worker_agenda_sync import process_agenda_sync
from app.workers.worker_voice_orchestrator import process_voice_call

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
QUEUES = [
    "queue.mealplan.generation",
    "queue.messaging",
    "queue.human_escalation",
    "queue.ai_resume",
    "queue.campaigns",
    "queue.notifications",
    "queue.atendimento",
    "queue.agenda.sync",
    "queue.arquivo.dispatch",
    "queue.voice.call",
    "queue.admin.ops",
    "queue.specialist",
]


def active_queues() -> list[str]:
    configured = os.getenv("WORKER_QUEUES", "").strip()
    if not configured:
        return QUEUES
    selected = [q.strip() for q in configured.split(",") if q.strip()]
    return selected or QUEUES

_connection = None
_channel = None


def _init_connection():
    global _connection, _channel
    if _connection is not None and _channel is not None:
        return _channel

    try:
        _connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
        _channel = _connection.channel()
        for queue in active_queues():
            _channel.queue_declare(queue=queue)
        return _channel
    except Exception:
        _connection = None
        _channel = None
        return None


def send_message(queue: str, message: str):
    if os.getenv("TEST_ENV", "0") == "1":
        return True
    channel = _init_connection()
    if channel is None:
        # RabbitMQ não disponível; ignorar mensagem ou logar.
        return False
    channel.basic_publish(exchange="", routing_key=queue, body=message)
    return True


def get_queue_depth(queue: str) -> int | None:
    channel = _init_connection()
    if channel is None:
        return None
    try:
        q = channel.queue_declare(queue=queue, passive=True)
        return int(q.method.message_count)
    except Exception:
        return None


def process_message(queue, body):
    data = json.loads(body)

    if queue == "queue.atendimento":
        process_atendimento_workflow(data)
        return

    if queue == "queue.messaging":
        tenant_id = data.get("tenant_id")
        conversation_id = data.get("conversation_id")
        account_id = data.get("account_id")
        message = data.get("message")
        enviar_mensagens(account_id, conversation_id, [f"Processado: {message}"])
        return

    if queue == "queue.notifications":
        process_notification_event(data)
        return

    if queue == "queue.agenda.sync":
        process_agenda_sync(data)
        return

    if queue == "queue.arquivo.dispatch":
        process_arquivo_dispatch(data)
        return

    if queue == "queue.voice.call":
        process_voice_call(data)
        return

    if queue == "queue.admin.ops":
        process_admin_ops(data)
        return

    if queue == "queue.specialist":
        process_specialist_task(data)
        return

    # outras filas podem ser processadas conforme necessidade
    print(f"[rabbitmq_worker] fila não gerenciada: {queue}")


def consume_all_queues():
    channel = _init_connection()
    if channel is None:
        print("RabbitMQ não disponível. Não será feito consume.")
        return

    def _callback(ch, method, properties, body):
        queue = method.routing_key
        process_message(queue, body)

    for queue in active_queues():
        channel.queue_declare(queue=queue, durable=True)
        channel.basic_consume(queue=queue, on_message_callback=_callback, auto_ack=True)

    print(' [*] Waiting for messages in all queues. To exit press CTRL+C')
    channel.start_consuming()


if __name__ == "__main__":
    try:
        consume_all_queues()
    except KeyboardInterrupt:
        print("Encerrando consumer RabbitMQ...")
