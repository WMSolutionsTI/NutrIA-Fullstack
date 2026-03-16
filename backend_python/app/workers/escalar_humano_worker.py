import requests
import os

CHATWOOT_URL = os.getenv("CHATWOOT_URL", "http://chatwoot:3000")
CHATWOOT_API_KEY = os.getenv("CHATWOOT_API_KEY", "your_api_key")

# Função para escalar humano (adicionar etiqueta, transferir conversa)
    url = f"{CHATWOOT_URL}/api/v1/accounts/{account_id}/conversations/{conversation_id}/labels"
    headers = {"api_access_token": CHATWOOT_API_KEY}
    data = {"labels": [label]}
    response = requests.post(url, headers=headers, json=data)
    return response.status_code == 200

# Exemplo de uso:
if __name__ == "__main__":
    account_id = 1
    conversation_id = 12345
    label = "humano"
    escalar_humano(account_id, conversation_id, label)