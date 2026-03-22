import json
import re
import secrets
from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.core.config import FRONTEND_URL
from app.db import get_db
from app.domain.models.caixa_de_entrada import CaixaDeEntrada
from app.domain.models.chatwoot_account import ChatwootAccount
from app.domain.models.cliente import Cliente
from app.domain.models.conversa import Conversa
from app.domain.models.nutri_contact_verification import NutriContactVerification
from app.services.conversation_archive_service import archive_conversa_snapshot
from app.services.event_bus import build_event_payload, publish_event
from app.services.worker_job_service import create_worker_job
from app.utils.text_normalize import normalize_pt_text
from app.workers.admin_monitor_worker import notificar_admins
from app.workers.cadastro_assinatura_worker import enviar_email_codigo_validacao_nutri
from app.workers.chatwoot_message_worker import enviar_mensagem_chatwoot
from app.workers.quebrar_enviar_mensagens_worker import enviar_mensagens


def is_request_nutricionista(message: str) -> bool:
    if not message or not isinstance(message, str):
        return False
    text = normalize_pt_text(message)
    triggers = [
        "falar com nutricionista",
        "atendimento humano",
        "atendimento com nutricionista",
        "quero falar com a nutricionista",
        "preciso de nutricionista",
        "urgente nutricionista",
        "vou falar diretamente com a nutricionista",
        "não quero ia",
        "sem ia",
        "atendimento direto"
    ]
    return any(trigger in text for trigger in triggers)


def is_finalizar_atendimento(message: str) -> bool:
    if not message or not isinstance(message, str):
        return False
    text = normalize_pt_text(message)
    triggers = [
        "encerrar atendimento",
        "finalizar atendimento",
        "retornar secretaria",
        "voltar para secretária",
        "demanda encerrada",
        "atendimento finalizado",
        "liberar secretaria",
        "retornar ao bot",
        "voltar para a secretária"
    ]
    return any(trigger in text for trigger in triggers)


def notificar_nutricionista(db: Session, cliente, nutricionista, conversation_id):
    link = f"{FRONTEND_URL}/nutricionista/clientes/{cliente.id}/conversas/{conversation_id}"
    mensagem = (
        f"[Escalonamento] Cliente {cliente.nome} (ID {cliente.id}) solicitou falar com nutricionista {nutricionista.nome}. "
        f"Acompanhe aqui: {link}"
    )
    contato_nutri = (
        db.query(Cliente)
        .filter(Cliente.nutricionista_id == nutricionista.id, Cliente.status == "nutri")
        .order_by(Cliente.id.asc())
        .first()
    )
    if not contato_nutri:
        return
    ultima = (
        db.query(Conversa)
        .filter(
            Conversa.cliente_id == contato_nutri.id,
            Conversa.chatwoot_account_id.isnot(None),
            Conversa.chatwoot_conversation_id.isnot(None),
        )
        .order_by(Conversa.id.desc())
        .first()
    )
    if not ultima:
        return
    enviar_mensagens(
        ultima.chatwoot_account_id,
        ultima.chatwoot_conversation_id,
        [mensagem],
    )


def parse_int_from_text(pattern: str, message: str) -> int | None:
    match = re.search(pattern, normalize_pt_text(message))
    if not match:
        return None
    value = match.group(1)
    return int(value) if value and value.isdigit() else None


def _archive_nova_conversa(
    caixa: CaixaDeEntrada | None, db: Session, nova_conversa: Conversa, tenant_id_fallback: int | None = None
) -> None:
    tenant_id = caixa.nutricionista.tenant_id if caixa and caixa.nutricionista else tenant_id_fallback
    archive_conversa_snapshot(db, conversa=nova_conversa, tenant_id=tenant_id)


def is_nutri_identification_phrase(message: str) -> bool:
    if not message or not isinstance(message, str):
        return False
    text = normalize_pt_text(message)
    return "sou a nutri" in text and "conta" in text


def parse_nutri_confirmation_code(message: str) -> str | None:
    if not message or not isinstance(message, str):
        return None
    match = re.search(r"\b(\d{6})\b", message)
    if not match:
        return None
    return match.group(1)


def _contains_any(message: str, triggers: list[str]) -> bool:
    text = normalize_pt_text(message)
    return any(trigger in text for trigger in triggers)


def _inferir_status_cliente(status_atual: str, message: str, interacoes: int) -> str:
    """
    Máquina de estados simplificada para automação de atendimento:
    - potencial -> ativo após continuidade de conversa
    - ativo/inativo -> satisfeito por sinais explícitos de sucesso
    - ativo/satisfeito -> inativo por pedido explícito de pausa/cancelamento
    """
    if status_atual in {"nutri", "em_atendimento_direto"}:
        return status_atual

    sinais_satisfacao = [
        "obrigado",
        "obrigada",
        "deu certo",
        "funcionou",
        "adorei",
        "estou satisfeito",
        "estou satisfeita",
        "resultado excelente",
    ]
    sinais_inatividade = [
        "não quero continuar",
        "nao quero continuar",
        "cancelar acompanhamento",
        "pausar atendimento",
        "vou parar por agora",
        "encerrar plano",
    ]

    if _contains_any(message, sinais_satisfacao):
        return "cliente_satisfeito"
    if _contains_any(message, sinais_inatividade):
        return "cliente_inativo"

    if status_atual == "cliente_potencial" and interacoes >= 2:
        return "cliente_ativo"

    return status_atual


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
    inbox_id = str(payload.get("inbox_id") or payload.get("inbox", "") or "")
    conversation_id = payload.get("conversation_id")
    account_id = str(payload.get("account_id") or "")
    message = payload.get("content") or payload.get("message", "")
    attachments_count = len(payload.get("attachments") or [])

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

    # Identificação canônica por account_id da conta Chatwoot.
    conta_chatwoot = None
    if account_id:
        conta_chatwoot = (
            db.query(ChatwootAccount)
            .filter(ChatwootAccount.chatwoot_account_external_id == account_id, ChatwootAccount.status == "active")
            .first()
        )
    if not conta_chatwoot and account_id:
        notificar_admins(f"[chatwoot] account_id sem mapeamento: {account_id}")
        return {"status": "account_unmapped", "account_id": account_id}
    if not conta_chatwoot:
        return {"status": "account_missing"}

    nutri_id = conta_chatwoot.nutricionista_id
    tenant_id = conta_chatwoot.tenant_id

    caixa = db.query(CaixaDeEntrada).filter(CaixaDeEntrada.identificador_chatwoot == inbox_id).first()
    if caixa and caixa.nutricionista_id != nutri_id:
        notificar_admins(
            f"[chatwoot] inconsistência account/inbox. account_id={account_id}, inbox_id={inbox_id}, "
            f"nutri_conta={nutri_id}, nutri_inbox={caixa.nutricionista_id}"
        )
        return {"status": "account_inbox_mismatch", "account_id": account_id, "inbox_id": inbox_id}
    canal_origem = (caixa.tipo if caixa else "desconhecido")
    nutri = conta_chatwoot.nutricionista

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
            nutricionista_id=nutri_id,
            historico=f"Início de contato pela inbox {inbox_id} / account {account_id}"
        )
        db.add(cliente)
        db.commit()
        db.refresh(cliente)

    # Atualiza link de nutricionista caso não vinculado
    if not cliente.nutricionista_id and nutri_id:
        cliente.nutricionista_id = nutri_id
        db.commit()
        db.refresh(cliente)

    # Cria conversa inicial para registro permanente
    contexto_nutri = getattr(nutri, "contexto_ia", None) if nutri else None
    nova_conversa = Conversa(
        cliente_id=cliente.id,
        nutricionista_id=nutri_id,
        caixa_id=caixa.id if caixa else None,
        chatwoot_account_id=account_id,
        chatwoot_inbox_id=inbox_id,
        canal_origem=canal_origem,
        chatwoot_conversation_id=str(conversation_id) if conversation_id is not None else None,
        mensagem=message or "<sem texto>",
        data=datetime.now(UTC),
        modo="ia",
        contexto_ia=contexto_nutri,
        em_conversa_direta=False
    )

    # Verifica última conversa para manter estado de atendimento direto
    ultima_conversa = db.query(Conversa).filter(Conversa.cliente_id == cliente.id).order_by(Conversa.id.desc()).first()
    direcao_ativa = bool(ultima_conversa and ultima_conversa.em_conversa_direta)

    # Fluxo especial: validação de contato "cliente tipo nutri"
    if nutri and is_nutri_identification_phrase(message):
        conta_numero = parse_int_from_text(r"conta\s*(?:numero|número)?\s*(\d+)", message)
        conta_chatwoot_num = (
            int(conta_chatwoot.chatwoot_account_external_id)
            if (conta_chatwoot.chatwoot_account_external_id or "").isdigit()
            else None
        )
        if conta_numero is not None and conta_chatwoot_num is not None and conta_numero != conta_chatwoot_num:
            enviar_mensagem_chatwoot(
                account_id,
                conversation_id,
                "Número da conta inválido para esta inbox. Verifique e tente novamente.",
            )
            return {"status": "nutri_identificacao_invalida", "cliente_id": cliente.id}

        codigo = f"{secrets.randbelow(900000) + 100000}"
        verificacao = NutriContactVerification(
            nutricionista_id=nutri.id,
            contato_chatwoot=str(contact_id or "desconhecido"),
            codigo=codigo,
            status="pending",
            expiracao_em=datetime.now(UTC) + timedelta(minutes=15),
            tentativas=0,
            criado_em=datetime.now(UTC),
        )
        db.add(verificacao)
        db.commit()

        enviar_email_codigo_validacao_nutri(
            email=nutri.email,
            nome=nutri.nome,
            codigo=codigo,
        )
        enviar_mensagem_chatwoot(
            account_id,
            conversation_id,
            "Me informe o código enviado para seu e-mail para confirmar este contato da nutri.",
        )
        return {"status": "nutri_verificacao_iniciada", "cliente_id": cliente.id}

    if nutri and contact_id:
        codigo_informado = parse_nutri_confirmation_code(message)
        if codigo_informado:
            verificacao = (
                db.query(NutriContactVerification)
                .filter(
                    NutriContactVerification.nutricionista_id == nutri.id,
                    NutriContactVerification.contato_chatwoot == str(contact_id),
                    NutriContactVerification.status == "pending",
                )
                .order_by(NutriContactVerification.id.desc())
                .first()
            )
            if verificacao:
                expiracao_em = verificacao.expiracao_em
                if expiracao_em and expiracao_em.tzinfo is None:
                    expiracao_em = expiracao_em.replace(tzinfo=UTC)

                if expiracao_em and datetime.now(UTC) > expiracao_em:
                    verificacao.status = "expired"
                    db.commit()
                    enviar_mensagem_chatwoot(
                        account_id,
                        conversation_id,
                        "Código expirado. Reenvie a frase de identificação para gerar um novo código.",
                    )
                    return {"status": "nutri_codigo_expirado", "cliente_id": cliente.id}

                verificacao.tentativas = int(verificacao.tentativas or 0) + 1
                if verificacao.codigo == codigo_informado:
                    verificacao.status = "validated"
                    verificacao.validado_em = datetime.now(UTC)
                    cliente.status = "nutri"
                    db.add(cliente)
                    db.add(verificacao)
                    db.commit()
                    enviar_mensagem_chatwoot(
                        account_id,
                        conversation_id,
                        "Contato confirmado com sucesso como cliente do tipo nutri.",
                    )
                    return {"status": "nutri_verificada", "cliente_id": cliente.id}

                if verificacao.tentativas >= 5:
                    verificacao.status = "blocked"
                    db.add(verificacao)
                    db.commit()
                    enviar_mensagem_chatwoot(
                        account_id,
                        conversation_id,
                        "Muitas tentativas inválidas. Solicite um novo código.",
                    )
                    return {"status": "nutri_codigo_bloqueado", "cliente_id": cliente.id}

                db.add(verificacao)
                db.commit()
                enviar_mensagem_chatwoot(
                    account_id,
                    conversation_id,
                    "Código inválido. Tente novamente.",
                )
                return {"status": "nutri_codigo_invalido", "cliente_id": cliente.id}

    db.add(nova_conversa)
    db.commit()
    _archive_nova_conversa(caixa, db, nova_conversa, tenant_id_fallback=tenant_id)

    # Conta admin: roteia mensagens para o worker operacional do cluster.
    if nutri and nutri.papel == "admin":
        event = build_event_payload(
            queue_tipo="admin_ops_chatwoot",
            tenant_id=tenant_id,
            nutricionista_id=nutri_id,
            cliente_id=cliente.id,
            payload={
                "source": "chatwoot_admin",
                "account_id": account_id,
                "inbox_id": inbox_id,
                "canal": canal_origem,
                "conversation_id": str(conversation_id) if conversation_id is not None else None,
                "message": message or "",
                "conversa_id": nova_conversa.id,
            },
        )
        publish_event("queue.admin.ops", event)
        create_worker_job(
            db,
            event_id=event["event_id"],
            queue="queue.admin.ops",
            tipo="admin_ops_chatwoot",
            tenant_id=tenant_id,
            nutricionista_id=nutri_id,
            cliente_id=cliente.id,
            payload=event,
        )
        return {"status": "queued_admin_ops", "cliente_id": cliente.id, "event_id": event["event_id"]}

    total_interacoes = (
        db.query(Conversa)
        .filter(Conversa.cliente_id == cliente.id)
        .count()
    )
    status_inferido = _inferir_status_cliente(cliente.status, message, total_interacoes)
    if status_inferido != cliente.status:
        cliente.status = status_inferido
        db.add(cliente)
        db.commit()

    event = build_event_payload(
        queue_tipo="chatwoot_message_received",
        tenant_id=tenant_id,
        nutricionista_id=nutri_id,
        cliente_id=cliente.id,
        payload={
            "account_id": account_id,
            "inbox_id": inbox_id,
            "canal": canal_origem,
            "conversation_id": str(conversation_id) if conversation_id is not None else None,
            "message": message,
            "attachments_count": attachments_count,
            "cliente_status": cliente.status,
            "retry_count": 0,
            "conversa_id": nova_conversa.id,
            "direct_mode_active": direcao_ativa,
        },
    )
    publish_event("queue.atendimento", event)
    create_worker_job(
        db,
        event_id=event["event_id"],
        queue="queue.atendimento",
        tipo="chatwoot_message_received",
        tenant_id=tenant_id,
        nutricionista_id=nutri_id,
        cliente_id=cliente.id,
        payload=event,
    )
    return {"status": "queued_ai", "cliente_id": cliente.id, "event_id": event["event_id"]}
