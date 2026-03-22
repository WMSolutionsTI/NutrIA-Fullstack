from datetime import UTC, datetime, timedelta
import json
import os
import re
import secrets
import uuid

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.domain.models.agenda_evento import AgendaEvento
from app.domain.models.arquivo import Arquivo
from app.domain.models.cliente import Cliente
from app.domain.models.contabilidade import Contabilidade
from app.domain.models.nutri_action_confirmation import NutriActionConfirmation
from app.domain.models.nutricionista import Nutricionista
from app.domain.models.plano_alimentar import PlanoAlimentar
from app.domain.models.voice_call import VoiceCall
from app.services.ai_service import gerar_resposta_agente
from app.services.event_bus import build_event_payload, publish_event
from app.services.worker_job_service import create_worker_job
from app.workers.chatwoot_attachment_worker import enviar_arquivo_chatwoot
from app.workers.minio_worker import download_object
from app.workers.quebrar_enviar_mensagens_worker import enviar_mensagens


SUPPORTED_ACTIONS = {
    "send_meal_plan_copy",
    "call_client",
    "send_voice_message",
    "summarize_financial",
    "list_clients_summary",
    "list_today_appointments",
    "delegate_specialist",
    "ask_clarification",
    "unknown",
}

SENSITIVE_ACTIONS = {
    "send_meal_plan_copy",
    "call_client",
    "send_voice_message",
    "delegate_specialist",
}

CONFIRMATION_TTL_MINUTES = 10
CONFIDENCE_THRESHOLD = 0.70


def _extrair_json(texto: str) -> dict:
    if not texto:
        return {}
    texto = texto.strip()
    try:
        parsed = json.loads(texto)
        return parsed if isinstance(parsed, dict) else {}
    except Exception:
        pass
    match = re.search(r"\{.*\}", texto, flags=re.DOTALL)
    if not match:
        return {}
    try:
        parsed = json.loads(match.group(0))
        return parsed if isinstance(parsed, dict) else {}
    except Exception:
        return {}


def _decidir_intencao_nutri(comando: str, contexto: str | None) -> dict:
    prompt = f"""
Você recebe pedido da nutricionista para a secretária virtual.
Responda SOMENTE JSON válido.

Schema:
{{
  "action": "send_meal_plan_copy" | "call_client" | "send_voice_message" | "summarize_financial" | "list_clients_summary" | "list_today_appointments" | "delegate_specialist" | "ask_clarification" | "unknown",
  "client_name": "string ou vazio",
  "message": "string ou vazio",
  "period": "this_month|today|custom|empty",
  "specialist": "agenda|financeiro|plano|atendimento|operacoes|empty",
  "objective": "string ou vazio",
  "confidence": 0.0
}}

Regras:
- Nunca invente cliente.
- Se intenção estiver ambígua, use action="ask_clarification".
- Se não for sua competência, use action="delegate_specialist".

Contexto da nutri:
{contexto or ""}

Mensagem:
{comando}
"""
    resposta = gerar_resposta_agente("suporte_nutri", prompt, contexto=contexto, model="gpt-4o-mini", temperature=0.1)
    parsed = _extrair_json(resposta)
    action = str(parsed.get("action", "unknown")).strip()
    if action not in SUPPORTED_ACTIONS:
        action = "unknown"
    return {
        "action": action,
        "client_name": str(parsed.get("client_name", "") or "").strip(),
        "message": str(parsed.get("message", "") or "").strip(),
        "period": str(parsed.get("period", "") or "").strip(),
        "specialist": str(parsed.get("specialist", "") or "").strip(),
        "objective": str(parsed.get("objective", "") or "").strip(),
        "confidence": float(parsed.get("confidence", 0) or 0),
    }


def _buscar_cliente_por_nome(db: Session, nutri_id: int, nome: str | None) -> Cliente | None:
    if not nome:
        return None
    termo = nome.strip().lower()
    if not termo:
        return None
    return (
        db.query(Cliente)
        .filter(Cliente.nutricionista_id == nutri_id, func.lower(Cliente.nome).like(f"%{termo}%"))
        .order_by(Cliente.id.desc())
        .first()
    )


def _telefone_cliente(cliente: Cliente) -> str | None:
    contato = (cliente.contato_chatwoot or "").strip()
    digitos = "".join(ch for ch in contato if ch.isdigit())
    if len(digitos) < 10:
        return None
    if contato.startswith("+"):
        return contato
    return f"+{digitos}"


def _parse_confirmation_command(message: str) -> tuple[str | None, str | None]:
    texto = (message or "").strip().lower()
    m_confirm = re.search(r"\bconfirmo\s+([a-z0-9]{6,12})\b", texto)
    if m_confirm:
        return "confirm", m_confirm.group(1).upper()
    m_cancel = re.search(r"\bcancelar\s+([a-z0-9]{6,12})\b", texto)
    if m_cancel:
        return "cancel", m_cancel.group(1).upper()
    return None, None


def _pending_confirmation(db: Session, nutri_id: int, account_id: str, conversation_id: str):
    now_utc = datetime.now(UTC).replace(tzinfo=None)
    pending = (
        db.query(NutriActionConfirmation)
        .filter(
            NutriActionConfirmation.nutricionista_id == nutri_id,
            NutriActionConfirmation.account_id == str(account_id),
            NutriActionConfirmation.conversation_id == str(conversation_id),
            NutriActionConfirmation.status == "pending",
        )
        .order_by(NutriActionConfirmation.id.desc())
        .first()
    )
    if not pending:
        return None
    if pending.expires_em and pending.expires_em < now_utc:
        pending.status = "expired"
        pending.atualizado_em = now_utc
        db.add(pending)
        db.commit()
        return None
    return pending


def _open_confirmation(
    db: Session,
    *,
    nutri: Nutricionista,
    account_id: str,
    conversation_id: str,
    action_payload: dict,
) -> NutriActionConfirmation:
    atual = _pending_confirmation(db, nutri.id, account_id, conversation_id)
    now_utc = datetime.now(UTC).replace(tzinfo=None)
    if atual:
        atual.status = "cancelled"
        atual.atualizado_em = now_utc
        db.add(atual)
        db.commit()

    token = (secrets.token_hex(3)).upper()
    confirmation = NutriActionConfirmation(
        tenant_id=nutri.tenant_id,
        nutricionista_id=nutri.id,
        account_id=str(account_id),
        conversation_id=str(conversation_id),
        token=token,
        status="pending",
        action_payload=json.dumps(action_payload, ensure_ascii=False),
        expires_em=now_utc + timedelta(minutes=CONFIRMATION_TTL_MINUTES),
        criado_em=now_utc,
        atualizado_em=now_utc,
    )
    db.add(confirmation)
    db.commit()
    db.refresh(confirmation)
    return confirmation


def _resumo_confirmacao(action_payload: dict, cliente: Cliente | None) -> str:
    action = action_payload.get("action", "unknown")
    objective = action_payload.get("objective") or ""
    if action == "send_meal_plan_copy":
        return f"Enviar cópia de plano alimentar para a cliente {cliente.nome if cliente else '-'}."
    if action == "call_client":
        return f"Ligar para a cliente {cliente.nome if cliente else '-'}."
    if action == "send_voice_message":
        return f"Enviar mensagem de voz para {cliente.nome if cliente else '-'}."
    if action == "delegate_specialist":
        return f"Delegar para especialista ({action_payload.get('specialist') or 'atendimento'}). Objetivo: {objective}"
    return f"Executar ação {action}."


def _enfileirar_ligacao(
    db: Session,
    *,
    nutri: Nutricionista,
    cliente: Cliente,
    account_id: str,
    conversation_id: str,
    objetivo: str,
) -> VoiceCall | None:
    telefone = _telefone_cliente(cliente)
    if not telefone:
        return None

    chamada = VoiceCall(
        tenant_id=nutri.tenant_id,
        nutricionista_id=nutri.id,
        cliente_id=cliente.id,
        telefone_destino=telefone,
        status="queued",
        resumo=objetivo,
        criado_em=datetime.utcnow(),
        atualizado_em=datetime.utcnow(),
    )
    db.add(chamada)
    db.commit()
    db.refresh(chamada)

    event = build_event_payload(
        queue_tipo="voice_call_create",
        tenant_id=nutri.tenant_id,
        nutricionista_id=nutri.id,
        cliente_id=cliente.id,
        payload={
            "voice_call_id": chamada.id,
            "telefone_destino": telefone,
            "account_id": account_id,
            "conversation_id": conversation_id,
            "objective": objetivo,
        },
    )
    publish_event("queue.voice.call", event)
    create_worker_job(
        db,
        event_id=event["event_id"],
        queue="queue.voice.call",
        tipo="voice_call_create",
        tenant_id=nutri.tenant_id,
        nutricionista_id=nutri.id,
        cliente_id=cliente.id,
        payload=event,
    )
    return chamada


def _enfileirar_mensagem_voz(
    db: Session,
    *,
    nutri: Nutricionista,
    cliente: Cliente,
    account_id: str,
    conversation_id: str,
    mensagem: str,
) -> None:
    event = build_event_payload(
        queue_tipo="voice_message_chatwoot",
        tenant_id=nutri.tenant_id,
        nutricionista_id=nutri.id,
        cliente_id=cliente.id,
        payload={
            "account_id": account_id,
            "conversation_id": conversation_id,
            "cliente_id": cliente.id,
            "cliente_nome": cliente.nome,
            "text": mensagem,
        },
    )
    publish_event("queue.voice.call", event)
    create_worker_job(
        db,
        event_id=event["event_id"],
        queue="queue.voice.call",
        tipo="voice_message_chatwoot",
        tenant_id=nutri.tenant_id,
        nutricionista_id=nutri.id,
        cliente_id=cliente.id,
        payload=event,
    )


def _resumo_financeiro_mes(db: Session, tenant_id: int) -> str:
    inicio_mes = datetime.now(UTC).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    receitas = (
        db.query(Contabilidade)
        .filter(Contabilidade.tenant_id == tenant_id, Contabilidade.tipo == "receita", Contabilidade.data >= inicio_mes)
        .all()
    )
    despesas = (
        db.query(Contabilidade)
        .filter(Contabilidade.tenant_id == tenant_id, Contabilidade.tipo == "despesa", Contabilidade.data >= inicio_mes)
        .all()
    )
    total_receitas = sum(float(r.valor or 0) for r in receitas)
    total_despesas = sum(float(d.valor or 0) for d in despesas)
    saldo = total_receitas - total_despesas
    return (
        f"Resumo financeiro do mês:\n"
        f"Receitas: R$ {total_receitas:.2f}\n"
        f"Despesas: R$ {total_despesas:.2f}\n"
        f"Saldo: R$ {saldo:.2f}"
    )


def _resumo_clientes(db: Session, nutri_id: int) -> str:
    total_clientes = db.query(Cliente).filter(Cliente.nutricionista_id == nutri_id).count()
    ativos = db.query(Cliente).filter(Cliente.nutricionista_id == nutri_id, Cliente.status == "cliente_ativo").count()
    potenciais = db.query(Cliente).filter(Cliente.nutricionista_id == nutri_id, Cliente.status == "cliente_potencial").count()
    return (
        f"Resumo de clientes:\n"
        f"Total: {total_clientes}\n"
        f"Ativos: {ativos}\n"
        f"Potenciais: {potenciais}"
    )


def _agenda_hoje(db: Session, nutri_id: int) -> str:
    inicio = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)
    fim = datetime.now(UTC).replace(hour=23, minute=59, second=59, microsecond=999999)
    eventos = (
        db.query(AgendaEvento)
        .filter(
            AgendaEvento.nutricionista_id == nutri_id,
            AgendaEvento.inicio_em >= inicio,
            AgendaEvento.inicio_em <= fim,
            AgendaEvento.status != "cancelado",
        )
        .order_by(AgendaEvento.inicio_em.asc())
        .all()
    )
    if not eventos:
        return "Hoje não há consultas agendadas."
    linhas = []
    for ev in eventos:
        horario = ev.inicio_em.strftime("%H:%M") if ev.inicio_em else "--:--"
        linhas.append(f"- {horario} | {ev.titulo}")
    return "Consultas de hoje:\n" + "\n".join(linhas)


def _enviar_copia_plano_alimentar(
    db: Session,
    *,
    nutri: Nutricionista,
    account_id: str,
    conversation_id: str,
    cliente: Cliente,
) -> None:
    plano = (
        db.query(PlanoAlimentar)
        .filter(PlanoAlimentar.nutricionista_id == nutri.id, PlanoAlimentar.cliente_id == cliente.id)
        .order_by(PlanoAlimentar.data_atualizacao.desc().nullslast(), PlanoAlimentar.id.desc())
        .first()
    )
    if not plano:
        enviar_mensagens(account_id, conversation_id, [f"Não encontrei plano alimentar cadastrado para {cliente.nome}."])
        return

    arquivo = (
        db.query(Arquivo)
        .filter(
            Arquivo.cliente_id == cliente.id,
            Arquivo.tenant_id == nutri.tenant_id,
            Arquivo.tipo == "documento",
            func.lower(Arquivo.nome).like("%plano%"),
        )
        .order_by(Arquivo.id.desc())
        .first()
    )

    resumo_prompt = (
        "Resuma em até 5 linhas, sem conteúdo sensível além do necessário para a nutricionista.\n"
        f"Título: {plano.titulo}\n"
        f"Descrição: {plano.descricao or ''}\n"
        f"Macros: {plano.macros or ''}\n"
        f"Refeições: {plano.refeicoes or ''}\n"
    )
    resumo = gerar_resposta_agente("secretaria", resumo_prompt, contexto=nutri.contexto_ia, model="gpt-4o-mini", temperature=0.2)

    if arquivo:
        local_path = f"/tmp/{uuid.uuid4()}_{arquivo.nome}"
        try:
            if download_object(arquivo.caminho_s3, local_path) and enviar_arquivo_chatwoot(account_id, conversation_id, local_path):
                enviar_mensagens(account_id, conversation_id, [f"Enviei a cópia do plano alimentar de {cliente.nome}. {resumo}"])
                return
        finally:
            if os.path.exists(local_path):
                os.remove(local_path)

    enviar_mensagens(
        account_id,
        conversation_id,
        [f"Não localizei arquivo do plano para envio automático. Segue cópia textual do plano de {cliente.nome}:\n{resumo}"],
    )


def _delegar_especialista(
    db: Session,
    *,
    nutri: Nutricionista,
    cliente_id: int | None,
    account_id: str,
    conversation_id: str,
    specialist: str,
    objective: str,
    original_message: str,
) -> None:
    event = build_event_payload(
        queue_tipo="specialist_task",
        tenant_id=nutri.tenant_id,
        nutricionista_id=nutri.id,
        cliente_id=cliente_id,
        payload={
            "specialist": specialist or "atendimento",
            "objective": objective or "Atender solicitação da nutricionista.",
            "original_message": original_message,
            "account_id": account_id,
            "conversation_id": conversation_id,
            "contexto_nutri": nutri.contexto_ia or "",
        },
    )
    publish_event("queue.specialist", event)
    create_worker_job(
        db,
        event_id=event["event_id"],
        queue="queue.specialist",
        tipo="specialist_task",
        tenant_id=nutri.tenant_id,
        nutricionista_id=nutri.id,
        cliente_id=cliente_id,
        payload=event,
    )


def _executar_acao(
    db: Session,
    *,
    nutri: Nutricionista,
    account_id: str,
    conversation_id: str,
    action_payload: dict,
) -> None:
    action = action_payload.get("action", "unknown")
    client_name = action_payload.get("client_name") or ""
    cliente = _buscar_cliente_por_nome(db, nutri.id, client_name) if client_name else None

    if action == "send_meal_plan_copy":
        if not cliente:
            enviar_mensagens(account_id, conversation_id, ["Para enviar a cópia do plano, me confirme o nome da cliente no cadastro."])
            return
        _enviar_copia_plano_alimentar(db, nutri=nutri, account_id=account_id, conversation_id=conversation_id, cliente=cliente)
        return

    if action == "call_client":
        if not cliente:
            enviar_mensagens(account_id, conversation_id, ["Não consegui identificar a cliente para ligação. Informe o nome completo no cadastro."])
            return
        objetivo = action_payload.get("objective") or "Ligar para cliente para alinhamento solicitado pela nutricionista."
        chamada = _enfileirar_ligacao(
            db,
            nutri=nutri,
            cliente=cliente,
            account_id=account_id,
            conversation_id=conversation_id,
            objetivo=objetivo,
        )
        if not chamada:
            enviar_mensagens(account_id, conversation_id, ["Não foi possível iniciar a ligação. Verifique o telefone cadastrado da cliente."])
            return
        enviar_mensagens(account_id, conversation_id, [f"Ligação enfileirada para {cliente.nome}. Protocolo #{chamada.id}."])
        return

    if action == "send_voice_message":
        if not cliente:
            enviar_mensagens(account_id, conversation_id, ["Não consegui identificar a cliente para mensagem de voz."])
            return
        mensagem = (action_payload.get("message") or "").strip()
        if not mensagem:
            enviar_mensagens(account_id, conversation_id, ["Me diga o conteúdo da mensagem de voz que devo enviar."])
            return
        _enfileirar_mensagem_voz(db, nutri=nutri, cliente=cliente, account_id=account_id, conversation_id=conversation_id, mensagem=mensagem)
        enviar_mensagens(account_id, conversation_id, [f"Mensagem de voz enfileirada para {cliente.nome}."])
        return

    if action == "summarize_financial":
        enviar_mensagens(account_id, conversation_id, [_resumo_financeiro_mes(db, nutri.tenant_id)])
        return

    if action == "list_clients_summary":
        enviar_mensagens(account_id, conversation_id, [_resumo_clientes(db, nutri.id)])
        return

    if action == "list_today_appointments":
        enviar_mensagens(account_id, conversation_id, [_agenda_hoje(db, nutri.id)])
        return

    if action == "delegate_specialist":
        _delegar_especialista(
            db,
            nutri=nutri,
            cliente_id=cliente.id if cliente else None,
            account_id=account_id,
            conversation_id=conversation_id,
            specialist=action_payload.get("specialist") or "atendimento",
            objective=action_payload.get("objective") or "",
            original_message=action_payload.get("original_message") or "",
        )
        enviar_mensagens(account_id, conversation_id, ["Encaminhei sua solicitação para o agente especialista e retorno com atualização em seguida."])
        return

    if action == "ask_clarification":
        enviar_mensagens(account_id, conversation_id, ["Entendi parcialmente. Confirme o nome da cliente e o resultado esperado para eu executar com segurança."])
        return

    enviar_mensagens(account_id, conversation_id, ["Não consegui executar com segurança. Reformule o pedido com objetivo e cliente."])


def process_comando_chatwoot(account_id, conversation_id, comando, nutri_id, db: Session):
    nutri = db.query(Nutricionista).filter(Nutricionista.id == nutri_id).first()
    if not nutri:
        enviar_mensagens(account_id, conversation_id, ["Não consegui localizar sua conta. Tente novamente em instantes."])
        return

    account_id = str(account_id or "")
    conversation_id = str(conversation_id or "")
    comando_raw = (comando or "").strip()

    # 1) confirmação/cancelamento de ação pendente
    confirm_action, token = _parse_confirmation_command(comando_raw)
    if confirm_action and token:
        pending = _pending_confirmation(db, nutri.id, account_id, conversation_id)
        if not pending or pending.token != token:
            enviar_mensagens(account_id, conversation_id, ["Token de confirmação inválido ou expirado."])
            return
        now_utc = datetime.now(UTC).replace(tzinfo=None)
        if confirm_action == "cancel":
            pending.status = "cancelled"
            pending.atualizado_em = now_utc
            db.add(pending)
            db.commit()
            enviar_mensagens(account_id, conversation_id, ["Ação cancelada com sucesso."])
            return
        pending.status = "confirmed"
        pending.atualizado_em = now_utc
        db.add(pending)
        db.commit()
        action_payload = _extrair_json(pending.action_payload)
        _executar_acao(
            db,
            nutri=nutri,
            account_id=account_id,
            conversation_id=conversation_id,
            action_payload=action_payload,
        )
        return

    # 2) decisão por IA
    decisao = _decidir_intencao_nutri(comando_raw, nutri.contexto_ia)
    decisao["original_message"] = comando_raw
    action = decisao.get("action", "unknown")
    confidence = float(decisao.get("confidence", 0) or 0)
    client_name = decisao.get("client_name") or ""
    cliente = _buscar_cliente_por_nome(db, nutri.id, client_name) if client_name else None

    # 3) low-confidence nunca autoexecuta ação sensível
    if action in SENSITIVE_ACTIONS and (confidence < CONFIDENCE_THRESHOLD or (client_name and not cliente)):
        enviar_mensagens(
            account_id,
            conversation_id,
            ["Preciso de confirmação adicional para executar com segurança. Informe o nome exato da cliente e o objetivo."],
        )
        return

    # 4) ações sensíveis exigem confirmação explícita com token
    if action in SENSITIVE_ACTIONS:
        confirmation = _open_confirmation(
            db,
            nutri=nutri,
            account_id=account_id,
            conversation_id=conversation_id,
            action_payload=decisao,
        )
        resumo = _resumo_confirmacao(decisao, cliente)
        enviar_mensagens(
            account_id,
            conversation_id,
            [
                f"Confirma execução?\n{resumo}\n"
                f"Responda: `confirmo {confirmation.token}` para executar ou `cancelar {confirmation.token}` para abortar."
            ],
        )
        return

    # 5) ações não sensíveis executam direto
    _executar_acao(
        db,
        nutri=nutri,
        account_id=account_id,
        conversation_id=conversation_id,
        action_payload=decisao,
    )

