import os

import requests

CHATWOOT_URL = os.getenv("CHATWOOT_URL", "http://chatwoot:3000")
CHATWOOT_API_KEY = os.getenv("CHATWOOT_API_KEY", "your_api_key")


def escalar_humano(account_id: str | int, conversation_id: str | int, label: str = "humano") -> bool:
    """Adiciona label na conversa para sinalizar atendimento humano."""
    url = f"{CHATWOOT_URL}/api/v1/accounts/{account_id}/conversations/{conversation_id}/labels"
    headers = {"api_access_token": CHATWOOT_API_KEY}
    data = {"labels": [label]}
    response = requests.post(url, headers=headers, json=data, timeout=10)
    return response.status_code in {200, 201}


if __name__ == "__main__":
    escalar_humano(account_id=1, conversation_id=12345, label="humano")
