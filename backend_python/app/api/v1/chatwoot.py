from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.domain.models.cliente import Cliente
from app.db import get_db
from app.domain.models.caixa_de_entrada import CaixaDeEntrada
from app.domain.models.nutricionista import Nutricionista
from app.domain.repositories.tenant_repository import TenantRepository
from app.workers.rabbitmq_worker import send_message
from app.workers.quebrar_enviar_mensagens_worker import enviar_mensagens
from app.workers.suporte_nutri_worker import process_comando_chatwoot
from app.domain.models.tenant import Tenant
import json

router = APIRouter()

@router.post("/chatwoot/inbox/vincular")
def vincular_inbox_chatwoot(cliente_id: int, inbox_id: str, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    cliente.chatwoot_inbox_id = inbox_id
    db.commit()
    db.refresh(cliente)
    return cliente

@router.get("/chatwoot/mensagens")
def consultar_mensagens_chatwoot(cliente_id: int, db: Session = Depends(get_db)):
    # Mock: consulta de mensagens
    return {"cliente_id": cliente_id, "mensagens": ["msg1", "msg2"]}

@router.post("/chatwoot/webhook")
async def receber_webhook_chatwoot(request: Request, db: Session = Depends(get_db)):
    payload = await request.json()
    inbox_id = payload.get("inbox_id")
    conversation_id = payload.get("conversation_id")
    account_id = payload.get("account_id")
    message = payload.get("content")

    # Identifica o tenant
    tenant_repo = TenantRepository(db)
    tenant = tenant_repo.get_by_inbox_id(inbox_id)
    if not tenant:
        return {"error": "Tenant não encontrado", "inbox_id": inbox_id}

    # Identifica o nutricionista pela caixa de entrada
    caixa = db.query(CaixaDeEntrada).filter(CaixaDeEntrada.identificador_chatwoot == inbox_id).first()
    nutri = caixa.nutricionista if caixa else None

    # Verifica tipo_user antes de responder
    if nutri and nutri.tipo_user == "nutri" and message:
        from app.workers.suporte_nutri_worker import process_comando_chatwoot
        process_comando_chatwoot(account_id, conversation_id, message.strip().lower(), nutri.id, db)
        return {"status": "comando_processado", "nutricionista": nutri.nome, "tenant": tenant.nome}
    elif nutri and nutri.tipo_user != "nutri":
        return {"status": "acesso_negado", "motivo": "Usuário não autorizado para informações exclusivas"}

    # Lógica de decisão: exemplo simplificado
    if "responder" in message:
        # Responde diretamente via Chatwoot
        enviar_mensagens(account_id, conversation_id, ["Resposta automática: ok!"])
        return {"status": "respondido", "tenant": tenant.nome}
    elif "executar" in message:
        # Executa ação local (mock)
        resultado = {"acao": "executada", "tenant": tenant.nome}
        return {"status": "executado", "resultado": resultado}
    elif nutri and nutri.tipo_user == "cliente" and message:
        # Suporte ao cliente: responder dúvidas, pagamentos, agenda, follow-ups
        resposta = "Olá! Você está falando com a equipe da nutricionista {}. Como posso ajudar?".format(nutri.nome)
        # Aqui pode-se expandir para lógica de atendimento ao cliente
        from app.workers.quebrar_enviar_mensagens_worker import enviar_mensagens
        enviar_mensagens(account_id, conversation_id, [resposta])
        return {"status": "suporte_cliente", "cliente": nutri.nome, "tenant": tenant.nome}
    else:
        # Envia para fila RabbitMQ para processamento por worker
        send_message(json.dumps({"tenant_id": tenant.id, "conversation_id": conversation_id, "message": message}))
        return {"status": "enviado_para_fila", "tenant": tenant.nome}