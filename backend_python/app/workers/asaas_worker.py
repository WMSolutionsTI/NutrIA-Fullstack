import requests
import os

ASAAS_API_URL = os.getenv("ASAAS_API_URL", "https://www.asaas.com/api/v3")
ASAAS_API_KEY = os.getenv("ASAAS_API_KEY", "your_asaas_key")

# Função para criar cobrança

def criar_cobranca(cliente_id, valor, vencimento):
    url = f"{ASAAS_API_URL}/payments"
    headers = {"access_token": ASAAS_API_KEY, "Content-Type": "application/json"}
    data = {
        "customer": cliente_id,
        "value": valor,
        "dueDate": vencimento
    }
    from app.core.logging import logger
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        logger.info("Cobrança criada", extra={"data": response.json()})
        return response.json()
    else:
        logger.error("Erro ao criar cobrança", extra={"error": response.text})
        return None

# Função para consultar cobrança

def consultar_cobranca(cobranca_id):
    url = f"{ASAAS_API_URL}/payments/{cobranca_id}"
    headers = {"access_token": ASAAS_API_KEY}
    from app.core.logging import logger
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        logger.error("Erro ao consultar cobrança", extra={"error": response.text})
        return None

# Exemplo de uso:
if __name__ == "__main__":
    cliente_id = "cus_123"
    valor = 100.0
    vencimento = "2026-03-20"
    cobranca = criar_cobranca(cliente_id, valor, vencimento)
    if cobranca:
        consulta = consultar_cobranca(cobranca['id'])
        print("Consulta cobrança:", consulta)