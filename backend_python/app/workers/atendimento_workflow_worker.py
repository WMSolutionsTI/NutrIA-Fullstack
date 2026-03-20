import os
import uuid
from app.workers.quebrar_enviar_mensagens_worker import enviar_mensagens
from app.workers.chatwoot_attachment_worker import enviar_arquivo_chatwoot
from app.workers.minio_worker import download_object
from app.domain.models.arquivo import Arquivo
from app.db import SessionLocal


def process_file_transfer(arquivo_id, account_id, conversation_id):
    db = SessionLocal()
    try:
        arquivo = db.query(Arquivo).get(arquivo_id)
        if not arquivo:
            return {"status": "arquivo_nao_encontrado"}

        local_path = f"/tmp/{uuid.uuid4()}_{arquivo.nome}"
        if not download_object(arquivo.caminho_s3, local_path):
            return {"status": "falha_download"}

        enviado = enviar_arquivo_chatwoot(account_id, conversation_id, local_path)
        os.remove(local_path)
        return {"status": "arquivo_enviado" if enviado else "erro_envio"}
    finally:
        db.close()


def process_atendimento_workflow(payload):
    """Processa workflows de atendimento com base no tipo de cliente."""
    account_id = payload.get("account_id")
    conversation_id = payload.get("conversation_id")
    message = payload.get("message")
    workflow = payload.get("workflow")

    arquivo_id = payload.get("arquivo_id")
    if arquivo_id and account_id and conversation_id:
        file_result = process_file_transfer(arquivo_id, account_id, conversation_id)
        return {"status": "arquivo_transferido", "result": file_result}

    if workflow == "potencial":
        resposta = (
            "Olá! Sou a assistente virtual da sua nutricionista. "
            "Vou te ajudar com informações sobre planos, horários e especialidades. "
            "Qual a sua principal dúvida hoje?"
        )
    elif workflow == "ativo":
        resposta = (
            "Perfeito, vou continuar seu acompanhamento. "
            "Informe seus sintomas/níveis de progresso e vamos ajustar o plano nutricional."
        )
    elif workflow == "recuperacao":
        resposta = (
            "Estamos sentindo sua falta! Temos uma oferta especial para retomar seu acompanhamento. "
            "Quer conversar sobre o plano que estava usando?"
        )
    elif workflow == "manter_relacionamento":
        resposta = (
            "Parabéns pelos resultados! "
            "Temos novidades exclusivas e pesquisa de satisfação. Posso te enviar?"
        )
    else:
        resposta = "Recebido. Estamos processando sua solicitação e em breve te responderemos."

    if account_id and conversation_id:
        enviar_mensagens(account_id, conversation_id, [resposta])

    # Retornar objeto para testes se necessário
    return {
        "status": "ok",
        "workflow": workflow,
        "message": resposta
    }
