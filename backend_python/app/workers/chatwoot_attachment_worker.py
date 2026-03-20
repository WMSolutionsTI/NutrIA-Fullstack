import os
import requests
from app.core.logging import logger

CHATWOOT_URL = os.getenv("CHATWOOT_URL", "http://chatwoot:3000")
CHATWOOT_API_KEY = os.getenv("CHATWOOT_API_KEY", "your_api_key")


def enviar_arquivo_chatwoot(account_id: str, conversation_id: str, local_path: str):
    """Envia arquivo para conversa do Chatwoot como anexo (copy do repositório)."""
    if os.getenv("TEST_ENV", "0") == "1":
        logger.info("[TEST_ENV] simulando envio de anexo para Chatwoot", extra={"account_id": account_id, "conversation_id": conversation_id, "path": local_path})
        return True

    url = f"{CHATWOOT_URL}/api/v1/accounts/{account_id}/conversations/{conversation_id}/messages"
    headers = {"api_access_token": CHATWOOT_API_KEY}

    files = {"attachments[]": open(local_path, "rb")}
    data = {"content": "Segue anexo solicitado."}

    try:
        response = requests.post(url, headers=headers, files=files, data=data, timeout=20)
        if response.status_code in (200, 201):
            logger.info("Arquivo enviado para Chatwoot", extra={"account_id": account_id, "conversation_id": conversation_id, "status_code": response.status_code})
            return True
        logger.error("Falha ao enviar attachment para Chatwoot", extra={"status": response.status_code, "body": response.text})
        return False
    except Exception as ex:
        logger.error("Erro na chamada para Chatwoot", extra={"erro": str(ex)})
        return False
    finally:
        files["attachments[]"].close()
