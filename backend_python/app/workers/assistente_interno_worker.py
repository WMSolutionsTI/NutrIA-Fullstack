from app.workers.quebrar_enviar_mensagens_worker import enviar_mensagens

def process_assistente_interno(account_id, conversation_id, mensagem):
    """
    Processa mensagem do assistente interno, podendo ser chamado por fila ou outros workers.
    """
    enviar_mensagens(account_id, conversation_id, [mensagem])