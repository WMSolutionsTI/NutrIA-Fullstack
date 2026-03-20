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
    inbox_id = payload.get("inbox_id") or payload.get("inbox","")
    conversation_id = payload.get("conversation_id")
    account_id = payload.get("account_id")
    message = payload.get("content") or payload.get("message","")

    def parse_chatwoot_contact_id(payload_data):
        # Chatwoot pode enviar sender.id ou contact.id em diferentes eventos
        if payload_data is None:
            return None
        # payload pode ter estrutura {"sender": {"id": ...}, "contact": {"id": ...}}
        sender = payload_data.get("sender") or {}
        contact = payload_data.get("contact") or {}
        return sender.get("id") or contact.get("id") or payload_data.get("sender_id") or payload_data.get("contact_id")

    contact_id = parse_chatwoot_contact_id(payload)
    if not contact_id:
        # tentar por campos distintos antigos e números
        contact_id = payload.get("sender_id") or payload.get("contact_id") or payload.get("source_id")

    # Identifica a caixa de entrada (inbox) e tenant correspondente
    caixa = db.query(CaixaDeEntrada).filter(CaixaDeEntrada.identificador_chatwoot == inbox_id).first()
    if not caixa:
        return {"error": "Inbox não encontrada", "inbox_id": inbox_id}

    nutri = caixa.nutricionista

    # Se ainda não existir cliente, criar como potencial (vinculado ao nutricionista)
    cliente = None
    if contact_id:
        cliente = db.query(Cliente).filter(Cliente.contato_chatwoot == str(contact_id)).first()

    if not cliente:
        # cria cliente potencial vinculado ao nutricionista da inbox
        cliente = Cliente(
            nome=payload.get("sender_name") or payload.get("contact_name") or "Novo Contato", 
            contato_chatwoot=str(contact_id or "desconhecido"),
            status="cliente_potencial",
            nutricionista_id=caixa.nutricionista_id,
            historico=f"Início de contato pela inbox {inbox_id}"
        )
        db.add(cliente)
        db.commit()
        db.refresh(cliente)

    # Atualiza link de nutricionista caso não vinculado
    if not cliente.nutricionista_id and caixa.nutricionista_id:
        cliente.nutricionista_id = caixa.nutricionista_id
        db.commit()
        db.refresh(cliente)

    # Cria conversa inicial para registro permanente
    from app.domain.models.conversa import Conversa
    nova_conversa = Conversa(
        cliente_id=cliente.id,
        nutricionista_id=caixa.nutricionista_id,
        caixa_id=caixa.id,
        mensagem=message or "<sem texto>",
        modo="ia",
        contexto_ia=nutri.contexto_ia if nutri else None
    )
    db.add(nova_conversa)
    db.commit()

    # Tratamento por tipo de cliente
    status_cliente = cliente.status

    if status_cliente == "nutri":
        # Nutricionista enviando comando à secretaria interna
        if message and isinstance(message, str) and message.lower().startswith("sou a nutri id"):
            # Exemplo: "sou a nutri id 123"
            return {"status": "nutri_verificacao_iniciada", "message": "Código enviado por email (simulado)"}
        from app.workers.suporte_nutri_worker import process_comando_chatwoot
        process_comando_chatwoot(account_id, conversation_id, message.strip().lower(), nutri.id if nutri else None, db)
        return {"status": "nutri_comando", "cliente_status": status_cliente}

    if status_cliente == "cliente_potencial":
        # Envia fila de atendimento comercial para worker de potencial
        send_message("queue.atendimento", json.dumps({
            "tenant_id": caixa.nutricionista.tenant_id if caixa.nutricionista else None,
            "conversation_id": conversation_id,
            "cliente_id": cliente.id,
            "account_id": account_id,
            "message": message,
            "workflow": "potencial"
        }))
        return {"status": "potencial_em_atendimento", "cliente_id": cliente.id}

    if status_cliente == "cliente_ativo":
        send_message("queue.atendimento", json.dumps({
            "tenant_id": caixa.nutricionista.tenant_id if caixa.nutricionista else None,
            "conversation_id": conversation_id,
            "cliente_id": cliente.id,
            "account_id": account_id,
            "message": message,
            "workflow": "ativo"
        }))
        return {"status": "ativo_em_acompanhamento", "cliente_id": cliente.id}

    if status_cliente == "cliente_inativo":
        send_message("queue.atendimento", json.dumps({
            "tenant_id": caixa.nutricionista.tenant_id if caixa.nutricionista else None,
            "conversation_id": conversation_id,
            "cliente_id": cliente.id,
            "account_id": account_id,
            "message": message,
            "workflow": "recuperacao"
        }))
        return {"status": "inativo_recuperacao", "cliente_id": cliente.id}

    if status_cliente == "cliente_satisfeito":
        send_message("queue.atendimento", json.dumps({
            "tenant_id": caixa.nutricionista.tenant_id if caixa.nutricionista else None,
            "conversation_id": conversation_id,
            "cliente_id": cliente.id,
            "account_id": account_id,
            "message": message,
            "workflow": "manter_relacionamento"
        }))
        return {"status": "satisfeito_relacionamento", "cliente_id": cliente.id}

    # Ring fallback: se não reconhecido, processa comando basico e fila
    if "responder" in (message or ""):
        enviar_mensagens(account_id, conversation_id, ["Resposta automática: ok!"])
        return {"status": "respondido", "cliente_id": cliente.id}

    send_message("queue.atendimento", json.dumps({
        "tenant_id": caixa.nutricionista.tenant_id if caixa.nutricionista else None,
        "conversation_id": conversation_id,
        "cliente_id": cliente.id,
        "account_id": account_id,
        "message": message,
        "workflow": "fallback"
    }))
    return {"status": "encaminhado_para_fila", "cliente_id": cliente.id}