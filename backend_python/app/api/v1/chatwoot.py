from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.models.cliente import Cliente
from app.database import get_db

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
from app.domain.repositories.tenant_repository import TenantRepository
from app.workers.rabbitmq_worker import send_message
from app.workers.quebrar_enviar_mensagens_worker import enviar_mensagens
from app.domain.models.tenant import Tenant
from sqlalchemy.orm import Session
import json

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

    # Lógica de decisão: exemplo simplificado
    if "responder" in message:
        # Responde diretamente via Chatwoot
        enviar_mensagens(account_id, conversation_id, ["Resposta automática: ok!"])
        return {"status": "respondido", "tenant": tenant.nome}
    elif "executar" in message:
        # Executa ação local (mock)
        resultado = {"acao": "executada", "tenant": tenant.nome}
        return {"status": "executado", "resultado": resultado}
    else:
        # Envia para fila RabbitMQ para processamento por worker
        send_message(json.dumps({"tenant_id": tenant.id, "conversation_id": conversation_id, "message": message}))
        return {"status": "enviado_para_fila", "tenant": tenant.nome}