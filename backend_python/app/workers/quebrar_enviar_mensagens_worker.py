import requests
import os

CHATWOOT_URL = os.getenv("CHATWOOT_URL", "http://chatwoot:3000")
CHATWOOT_API_KEY = os.getenv("CHATWOOT_API_KEY", "your_api_key")

def quebrar_mensagens(mensagem, tamanho=400):
    """
    Quebra uma mensagem longa em partes menores para envio.
    """
    return [mensagem[i:i+tamanho] for i in range(0, len(mensagem), tamanho)]

def enviar_mensagens(account_id, conversation_id, mensagens):
    """
    Envia uma lista de mensagens para uma conversa do Chatwoot.
    """
    url = f"{CHATWOOT_URL}/api/v1/accounts/{account_id}/conversations/{conversation_id}/messages"
    headers = {"api_access_token": CHATWOOT_API_KEY}
    from app.core.logging import logger
    for msg in mensagens:
        if os.getenv("TEST_ENV", "0") == "1":
            logger.info("[TEST_ENV] simulando envio de mensagem", extra={"account_id": account_id, "conversation_id": conversation_id, "msg": msg})
            continue
        data = {"content": msg}
        try:
            response = requests.post(url, headers=headers, json=data, timeout=5)
            if response.status_code == 200:
                logger.info(f"Mensagem enviada", extra={"account_id": account_id, "conversation_id": conversation_id, "msg": msg})
            else:
                logger.error(f"Erro ao enviar mensagem", extra={"account_id": account_id, "conversation_id": conversation_id, "msg": msg, "error": response.text})
        except Exception as e:
            logger.error("Erro ao enviar mensagem (exceção)", extra={"account_id": account_id, "conversation_id": conversation_id, "msg": msg, "error": str(e)})

# Worker pode ser chamado por outros workers para enviar mensagens processadas