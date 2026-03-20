import os
import requests
from app.core.logging import logger

CHATWOOT_URL = os.getenv("CHATWOOT_URL", "http://chatwoot:3000")
CHATWOOT_API_KEY = os.getenv("CHATWOOT_API_KEY", "your_api_key")


def enviar_mensagem_chatwoot(account_id: str, conversation_id: str, conteudo: str, attachments: list = None):
    if os.getenv("TEST_ENV", "0") == "1":
        logger.info("[TEST_ENV] simulando mensagem Chatwoot", extra={"account_id": account_id, "conversation_id": conversation_id, "conteudo": conteudo})
        return True

    url = f"{CHATWOOT_URL}/api/v1/accounts/{account_id}/conversations/{conversation_id}/messages"
    headers = {
        "api_access_token": CHATWOOT_API_KEY,
    }

    data = {
        "content": conteudo,
    }

    files = None
    if attachments:
        files = []
        for path in attachments:
            try:
                files.append(("attachments[]", open(path, "rb")))
            except Exception as e:
                logger.error("Erro ao abrir attachment", extra={"path": path, "erro": str(e)})

    try:
        if files:
            response = requests.post(url, headers=headers, data=data, files=files, timeout=20)
        else:
            response = requests.post(url, headers=headers, json=data, timeout=20)

        if 200 <= response.status_code < 300:
            logger.info("Mensagem enviada ao Chatwoot", extra={"status": response.status_code})
            return True
        logger.error("Falha ao enviar mensagem ao Chatwoot", extra={"status": response.status_code, "body": response.text})
        return False
    except Exception as ex:
        logger.error("Erro na chamada Chatwoot", extra={"erro": str(ex)})
        return False
    finally:
        if files:
            for _, f in files:
                try:
                    f.close()
                except Exception:
                    pass
