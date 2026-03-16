import pika
import os
import json
from app.workers.quebrar_enviar_mensagens_worker import enviar_mensagens
# Adicione outros imports de processamento conforme necessário

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
QUEUES = [
    "queue.mealplan.generation",
    "queue.messaging",
    "queue.human_escalation",
    "queue.ai_resume",
    "queue.campaigns",
    "queue.notifications"
]

connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
channel = connection.channel()
for queue in QUEUES:
    channel.queue_declare(queue=queue)

    channel.basic_publish(exchange='', routing_key=queue, body=message)

def process_message(queue, body):
    data = json.loads(body)
    # Exemplo: delega para função conforme fila
    if queue == "queue.messaging":
        # Processa mensagem e responde via Chatwoot
        tenant_id = data.get("tenant_id")
        conversation_id = data.get("conversation_id")
        account_id = data.get("account_id")
        message = data.get("message")
        enviar_mensagens(account_id, conversation_id, [f"Processado: {message}"])
    # Adicione outros processamentos por fila
    else:
        pass  # Fila não implementada

def consume_all_queues():
    def _callback(ch, method, properties, body):
        queue = method.routing_key
        process_message(queue, body)
    for queue in QUEUES:
        channel.basic_consume(queue=queue, on_message_callback=_callback, auto_ack=True)
    print(' [*] Waiting for messages in all queues. To exit press CTRL+C')
    channel.start_consuming()