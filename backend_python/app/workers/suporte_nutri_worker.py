from datetime import UTC, datetime, timedelta
import json
import os
import re
import secrets
import uuid

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.v1.integracoes_google import get_valid_google_access_token
from app.core.config import FRONTEND_URL
from app.domain.models.agenda_evento import AgendaEvento
from app.domain.models.arquivo import Arquivo
from app.domain.models.cliente import Cliente
from app.domain.models.contabilidade import Contabilidade
from app.domain.models.conversa import Conversa
from app.domain.models.google_calendar_integration import GoogleCalendarIntegration
from app.domain.models.nutri_action_confirmation import NutriActionConfirmation
from app.domain.models.nutricionista import Nutricionista
from app.domain.models.plano_alimentar import PlanoAlimentar
from app.domain.models.voice_call import VoiceCall
from app.services.ai_service import gerar_resposta_agente
from app.services.event_bus import build_event_payload, publish_event
from app.services.google_calendar_service import update_google_event
from app.services.worker_job_service import create_worker_job
from app.utils.text_normalize import normalize_pt_text
from app.workers.admin_monitor_worker import notificar_admins
from app.workers.chatwoot_attachment_worker import enviar_arquivo_chatwoot
from app.workers.minio_worker import download_object
from app.workers.quebrar_enviar_mensagens_worker import enviar_mensagens


SUPPORTED_ACTIONS = {
    "send_meal_plan_copy",
    "call_client",
    "send_voice_message",
    "register_client",
    "register_and_contact_client",
    "summarize_financial",
    "list_clients_summary",
    "list_today_appointments",
    "list_schedule_by_date",
    "check_day_availability",
    "bulk_reschedule_tomorrow_nextweek_afternoon",
    "reschedule_consultations",
    "delegate_specialist",
    "ask_clarification",
    "unknown",
}

SENSITIVE_ACTIONS = {
    "send_meal_plan_copy",
    "call_client",
    "send_voice_message",
    "register_client",
    "register_and_contact_client",
    "bulk_reschedule_tomorrow_nextweek_afternoon",
    "reschedule_consultations",
    "delegate_specialist",
}

CONFIRMATION_TTL_MINUTES = 10
CONFIDENCE_THRESHOLD = 0.70


def _is_admin_escalation_request(message: str) -> bool:
    text = normalize_pt_text(message)
    if not text:
        return False
    triggers = [
        "falar com admin",
        "falar com o admin",
        "quero falar com admin",
        "quero falar com o admin",
        "chamar administrador",
        "suporte do sistema",
        "falar com suporte",
    ]
    return any(trigger in text for trigger in triggers)


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
  "action": "send_meal_plan_copy" | "call_client" | "send_voice_message" | "register_client" | "register_and_contact_client" | "summarize_financial" | "list_clients_summary" | "list_today_appointments" | "list_schedule_by_date" | "check_day_availability" | "bulk_reschedule_tomorrow_nextweek_afternoon" | "reschedule_consultations" | "delegate_specialist" | "ask_clarification" | "unknown",
  "client_name": "string ou vazio",
  "new_client_name": "string ou vazio",
  "new_client_contact": "string ou vazio",
  "new_client_status": "potencial|ativo|inativo|satisfeito|empty",
  "message": "string ou vazio",
  "period": "this_month|today|custom|empty",
  "source_date": "YYYY-MM-DD|today|tomorrow|next_week|empty",
  "target_date": "YYYY-MM-DD|today|tomorrow|next_week|empty",
  "target_period": "morning|afternoon|evening|same_time|empty",
  "scope": "all_on_source_date|single_client|empty",
  "specialist": "agenda|financeiro|plano|atendimento|operacoes|empty",
  "objective": "string ou vazio",
  "confidence": 0.0
}}

Regras:
- Nunca invente cliente.
- Para cliente não cadastrado: use register_client ou register_and_contact_client, exigindo nome, contato e status (potencial, ativo, inativo ou satisfeito).
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
        "new_client_name": str(parsed.get("new_client_name", "") or "").strip(),
        "new_client_contact": str(parsed.get("new_client_contact", "") or "").strip(),
        "new_client_status": str(parsed.get("new_client_status", "") or "").strip(),
        "message": str(parsed.get("message", "") or "").strip(),
        "period": str(parsed.get("period", "") or "").strip(),
        "source_date": str(parsed.get("source_date", "") or "").strip(),
        "target_date": str(parsed.get("target_date", "") or "").strip(),
        "target_period": str(parsed.get("target_period", "") or "").strip(),
        "scope": str(parsed.get("scope", "") or "").strip(),
        "specialist": str(parsed.get("specialist", "") or "").strip(),
        "objective": str(parsed.get("objective", "") or "").strip(),
        "confidence": float(parsed.get("confidence", 0) or 0),
    }


def _rule_based_decision_for_nutri(comando: str) -> dict | None:
    text = normalize_pt_text(comando)
    if not text:
        return None
    if "agenda" in text and ("quero ver" in text or "mostrar" in text or "me mostre" in text or "minha agenda" in text):
        source_date = "today"
        if "amanha" in text:
            source_date = "tomorrow"
        elif "proxima semana" in text or "semana que vem" in text:
            source_date = "next_week"
        else:
            m_iso = re.search(r"\b(\d{4}-\d{2}-\d{2})\b", text)
            m_br = re.search(r"\b(\d{2})/(\d{2})(?:/(\d{4}))?\b", text)
            if m_iso:
                source_date = m_iso.group(1)
            elif m_br:
                day = int(m_br.group(1))
                month = int(m_br.group(2))
                year = int(m_br.group(3)) if m_br.group(3) else datetime.now(UTC).year
                source_date = f"{year:04d}-{month:02d}-{day:02d}"

        target_period = ""
        if "manha" in text:
            target_period = "morning"
        elif "tarde" in text:
            target_period = "afternoon"
        elif "noite" in text:
            target_period = "evening"

        return {
            "action": "list_schedule_by_date",
            "client_name": "",
            "new_client_name": "",
            "new_client_contact": "",
            "new_client_status": "",
            "message": "",
            "period": "custom",
            "source_date": source_date,
            "target_date": "",
            "target_period": target_period,
            "scope": "",
            "specialist": "",
            "objective": "Listar agenda por data/período",
            "confidence": 0.98,
        }
    if "cadastre" in text or "cadastrar" in text or "novo cliente" in text or "contato com" in text:
        name = ""
        contact = ""
        status = ""
        objective = "Fazer contato e alinhar detalhes da consulta."
        m_nome = re.search(r"(?:nome|cliente)\s*[:\-]?\s*([a-zA-Z\s]{3,60})", comando, flags=re.IGNORECASE)
        if m_nome:
            name = m_nome.group(1).strip()
        elif "contato com" in text:
            m_com = re.search(r"contato com\s+([a-zA-Z\s]{3,60})", comando, flags=re.IGNORECASE)
            if m_com:
                name = m_com.group(1).strip()
        m_phone = re.search(r"(\+?\d[\d\-\s]{8,}\d)", comando)
        if m_phone:
            contact = m_phone.group(1).strip()
        m_email = re.search(r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)", comando)
        if m_email and not contact:
            contact = m_email.group(1).strip()
        if "inativo" in text:
            status = "inativo"
        elif "satisfeito" in text:
            status = "satisfeito"
        elif "ativo" in text:
            status = "ativo"
        elif "nao consultou" in text or "primeira consulta" in text or "potencial" in text:
            status = "potencial"
        action = "register_and_contact_client" if ("contat" in text or "acerte os detalhes" in text) else "register_client"
        return {
            "action": action,
            "client_name": "",
            "new_client_name": name,
            "new_client_contact": contact,
            "new_client_status": status,
            "message": "",
            "period": "custom",
            "source_date": "",
            "target_date": "",
            "target_period": "",
            "scope": "",
            "specialist": "",
            "objective": objective,
            "confidence": 0.92 if (name and contact and status) else 0.72,
        }
    if ("horario livre" in text or "horarios livres" in text or "agenda livre" in text or "disponibilidade" in text) and "dia" in text:
        source_date = "today"
        if "amanha" in text:
            source_date = "tomorrow"
        elif "proxima semana" in text or "semana que vem" in text:
            source_date = "next_week"
        else:
            m_iso = re.search(r"\b(\d{4}-\d{2}-\d{2})\b", text)
            m_br = re.search(r"\b(\d{2})/(\d{2})(?:/(\d{4}))?\b", text)
            if m_iso:
                source_date = m_iso.group(1)
            elif m_br:
                day = int(m_br.group(1))
                month = int(m_br.group(2))
                year = int(m_br.group(3)) if m_br.group(3) else datetime.now(UTC).year
                source_date = f"{year:04d}-{month:02d}-{day:02d}"
        return {
            "action": "check_day_availability",
            "client_name": "",
            "message": "",
            "period": "custom",
            "source_date": source_date,
            "target_date": "",
            "target_period": "",
            "scope": "",
            "specialist": "",
            "objective": "Consultar horários livres",
            "confidence": 0.98,
        }
    return None


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


def _normalize_contact(raw: str | None) -> str:
    text = (raw or "").strip()
    if not text:
        return ""
    digits = "".join(ch for ch in text if ch.isdigit())
    if len(digits) >= 10:
        return f"+{digits}"
    return text


def _normalize_client_status(raw: str | None) -> str:
    text = normalize_pt_text(raw)
    if text in {"ativo", "cliente ativo"}:
        return "cliente_ativo"
    if text in {"inativo", "cliente inativo"}:
        return "cliente_inativo"
    if text in {"satisfeito", "cliente satisfeito"}:
        return "cliente_satisfeito"
    if text in {"potencial", "nao consultou", "nao_consultou", "novo", "sem consulta"}:
        return "cliente_potencial"
    return "cliente_potencial"


def _upsert_new_client(
    db: Session,
    *,
    nutri: Nutricionista,
    nome: str,
    contato: str,
    status_raw: str,
) -> tuple[Cliente | None, str | None]:
    nome = (nome or "").strip()
    contato = _normalize_contact(contato)
    if len(nome) < 2:
        return None, "Nome do cliente é obrigatório."
    if len(contato) < 5:
        return None, "Contato do cliente é obrigatório (telefone/identificador)."
    status = _normalize_client_status(status_raw)

    existente_contato = db.query(Cliente).filter(Cliente.contato_chatwoot == contato).first()
    if existente_contato and existente_contato.nutricionista_id != nutri.id:
        return None, "Já existe cliente com este contato em outra conta."
    if existente_contato and existente_contato.nutricionista_id == nutri.id:
        existente_contato.nome = nome
        existente_contato.status = status
        existente_contato.historico = json.dumps(
            {
                "pre_cadastro": True,
                "updated_by": "nutri_chat_command",
                "updated_at": datetime.now(UTC).isoformat(),
            },
            ensure_ascii=False,
        )
        db.add(existente_contato)
        db.commit()
        db.refresh(existente_contato)
        return existente_contato, None

    novo = Cliente(
        nome=nome,
        contato_chatwoot=contato,
        status=status,
        nutricionista_id=nutri.id,
        historico=json.dumps(
            {
                "pre_cadastro": True,
                "created_by": "nutri_chat_command",
                "created_at": datetime.now(UTC).isoformat(),
            },
            ensure_ascii=False,
        ),
    )
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo, None


def _parse_confirmation_command(message: str) -> tuple[str | None, str | None]:
    texto = normalize_pt_text(message)
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
    if action == "register_client":
        return (
            f"Cadastrar novo cliente: {action_payload.get('new_client_name') or '-'} "
            f"({action_payload.get('new_client_contact') or '-'}) com status "
            f"{action_payload.get('new_client_status') or 'potencial'}."
        )
    if action == "register_and_contact_client":
        return (
            f"Cadastrar e contatar cliente: {action_payload.get('new_client_name') or '-'} "
            f"({action_payload.get('new_client_contact') or '-'}) com status "
            f"{action_payload.get('new_client_status') or 'potencial'}."
        )
    if action == "bulk_reschedule_tomorrow_nextweek_afternoon":
        return "Contatar clientes com consulta amanhã e remarcar para próxima semana no período da tarde."
    if action == "reschedule_consultations":
        source_date = action_payload.get("source_date") or "não informado"
        target_date = action_payload.get("target_date") or "não informado"
        target_period = action_payload.get("target_period") or "horário livre"
        scope = action_payload.get("scope") or "all_on_source_date"
        if scope == "single_client":
            return (
                f"Remarcar consulta da cliente {cliente.nome if cliente else '-'} "
                f"de {source_date} para {target_date} ({target_period})."
            )
        return f"Remarcar consultas de {source_date} para {target_date} ({target_period})."
    if action == "delegate_specialist":
        return f"Delegar para especialista ({action_payload.get('specialist') or 'atendimento'}). Objetivo: {objective}"
    return f"Executar ação {action}."


def _is_overlap(start_a: datetime, end_a: datetime, start_b: datetime, end_b: datetime) -> bool:
    return start_a < end_b and end_a > start_b


def _find_next_slot(day_start: datetime, duration: timedelta, occupied: list[tuple[datetime, datetime]]) -> tuple[datetime, datetime] | None:
    slot_start = day_start.replace(hour=13, minute=0, second=0, microsecond=0)
    day_end = day_start.replace(hour=19, minute=0, second=0, microsecond=0)
    step = timedelta(minutes=30)
    while slot_start + duration <= day_end:
        slot_end = slot_start + duration
        if all(not _is_overlap(slot_start, slot_end, busy_start, busy_end) for busy_start, busy_end in occupied):
            return slot_start, slot_end
        slot_start += step
    return None


def _next_week_monday(base: datetime) -> datetime:
    weekday = base.weekday()
    days_until_next_monday = (7 - weekday) or 7
    return (base + timedelta(days=days_until_next_monday)).replace(hour=0, minute=0, second=0, microsecond=0)


def _parse_date_token(date_token: str, now_utc: datetime) -> tuple[datetime, datetime] | None:
    token = (date_token or "").strip().lower()
    if not token or token == "empty":
        return None
    if token == "today":
        start = now_utc.replace(hour=0, minute=0, second=0, microsecond=0)
        return start, start.replace(hour=23, minute=59, second=59, microsecond=999999)
    if token == "tomorrow":
        start = (now_utc + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        return start, start.replace(hour=23, minute=59, second=59, microsecond=999999)
    if token == "next_week":
        start = _next_week_monday(now_utc)
        end = start + timedelta(days=6, hours=23, minutes=59, seconds=59, microseconds=999999)
        return start, end
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})$", token)
    if not m:
        return None
    try:
        dt = datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    except Exception:
        return None
    return dt.replace(hour=0, minute=0, second=0, microsecond=0), dt.replace(hour=23, minute=59, second=59, microsecond=999999)


def _candidate_target_days(target_date: str, now_utc: datetime) -> list[datetime]:
    token = (target_date or "").strip().lower()
    if token == "next_week":
        monday = _next_week_monday(now_utc)
        return [monday + timedelta(days=i) for i in range(5)]
    parsed = _parse_date_token(token, now_utc)
    if parsed:
        return [parsed[0]]
    return []


def _period_window(day: datetime, period: str, reference_start: datetime | None = None) -> tuple[datetime, datetime]:
    p = (period or "").strip().lower()
    if p == "morning":
        return day.replace(hour=8, minute=0, second=0, microsecond=0), day.replace(hour=12, minute=0, second=0, microsecond=0)
    if p == "afternoon":
        return day.replace(hour=13, minute=0, second=0, microsecond=0), day.replace(hour=19, minute=0, second=0, microsecond=0)
    if p == "evening":
        return day.replace(hour=18, minute=0, second=0, microsecond=0), day.replace(hour=22, minute=0, second=0, microsecond=0)
    if p == "same_time" and reference_start:
        start = day.replace(hour=reference_start.hour, minute=reference_start.minute, second=0, microsecond=0)
        return start, day.replace(hour=22, minute=0, second=0, microsecond=0)
    return day.replace(hour=8, minute=0, second=0, microsecond=0), day.replace(hour=19, minute=0, second=0, microsecond=0)


def _find_next_slot_in_window(
    window_start: datetime,
    window_end: datetime,
    duration: timedelta,
    occupied: list[tuple[datetime, datetime]],
) -> tuple[datetime, datetime] | None:
    step = timedelta(minutes=30)
    slot_start = window_start
    while slot_start + duration <= window_end:
        slot_end = slot_start + duration
        if all(not _is_overlap(slot_start, slot_end, busy_start, busy_end) for busy_start, busy_end in occupied):
            return slot_start, slot_end
        slot_start += step
    return None


def _latest_cliente_chat_route(db: Session, cliente_id: int) -> tuple[str | None, str | None]:
    conversa = (
        db.query(Conversa)
        .filter(
            Conversa.cliente_id == cliente_id,
            Conversa.chatwoot_account_id.isnot(None),
            Conversa.chatwoot_conversation_id.isnot(None),
        )
        .order_by(Conversa.id.desc())
        .first()
    )
    if not conversa:
        return None, None
    return conversa.chatwoot_account_id, conversa.chatwoot_conversation_id


def _remarcar_consultas_amanha_proxima_semana_tarde(
    db: Session,
    *,
    nutri: Nutricionista,
    account_id: str,
    conversation_id: str,
    source_date: str = "tomorrow",
    target_date: str = "next_week",
    target_period: str = "afternoon",
    scope: str = "all_on_source_date",
    cliente_alvo: Cliente | None = None,
) -> None:
    now_utc = datetime.now(UTC).replace(tzinfo=None)
    source_range = _parse_date_token(source_date, now_utc)
    if not source_range:
        enviar_mensagens(
            account_id,
            conversation_id,
            ["Não entendi a data de origem da remarcação. Informe em formato YYYY-MM-DD ou termos como today/tomorrow/next_week."],
        )
        return
    source_start, source_end = source_range

    q = db.query(AgendaEvento).filter(
        AgendaEvento.nutricionista_id == nutri.id,
        AgendaEvento.status != "cancelado",
        AgendaEvento.inicio_em >= source_start,
        AgendaEvento.inicio_em <= source_end,
    )
    if scope == "single_client" and cliente_alvo:
        q = q.filter(AgendaEvento.cliente_id == cliente_alvo.id)
    eventos = q.order_by(AgendaEvento.inicio_em.asc()).all()
    if not eventos:
        enviar_mensagens(
            account_id,
            conversation_id,
            ["Não encontrei consultas para os critérios informados na data de origem."],
        )
        return

    target_days = _candidate_target_days(target_date, now_utc)
    if not target_days:
        enviar_mensagens(
            account_id,
            conversation_id,
            ["Não entendi a data de destino. Informe uma data YYYY-MM-DD ou termos como tomorrow/next_week."],
        )
        return
    target_start = min(target_days).replace(hour=0, minute=0, second=0, microsecond=0)
    target_end = max(target_days).replace(hour=23, minute=59, second=59, microsecond=999999)
    ocupados_raw = (
        db.query(AgendaEvento)
        .filter(
            AgendaEvento.nutricionista_id == nutri.id,
            AgendaEvento.status != "cancelado",
            AgendaEvento.inicio_em >= target_start,
            AgendaEvento.inicio_em <= target_end,
        )
        .all()
    )
    occupied = [(ev.inicio_em, ev.fim_em) for ev in ocupados_raw if ev.inicio_em and ev.fim_em]

    integration = (
        db.query(GoogleCalendarIntegration)
        .filter(
            GoogleCalendarIntegration.nutricionista_id == nutri.id,
            GoogleCalendarIntegration.status == "active",
        )
        .first()
    )
    access_token = None
    if integration:
        try:
            access_token = get_valid_google_access_token(db, integration)
        except Exception as exc:
            notificar_admins(f"Falha ao obter token Google para remarcação em lote nutri_id={nutri.id}: {exc}")

    sucesso = 0
    falhas = 0
    notificadas = 0
    detalhes: list[str] = []

    for evento in eventos:
        duration = (evento.fim_em - evento.inicio_em) if (evento.fim_em and evento.inicio_em) else timedelta(minutes=60)
        allocated = None
        for day in target_days:
            window_start, window_end = _period_window(day, target_period, evento.inicio_em)
            candidate = _find_next_slot_in_window(window_start, window_end, duration, occupied)
            if candidate:
                allocated = candidate
                break
        if not allocated:
            falhas += 1
            detalhes.append(f"- Evento #{evento.id}: sem horário disponível para o destino informado.")
            continue

        novo_inicio, novo_fim = allocated
        evento.inicio_em = novo_inicio
        evento.fim_em = novo_fim
        evento.atualizado_em = now_utc
        db.add(evento)

        if integration and access_token and evento.google_event_id:
            try:
                update_google_event(
                    access_token,
                    calendar_id=integration.calendar_id or "primary",
                    google_event_id=evento.google_event_id,
                    titulo=evento.titulo,
                    descricao=evento.descricao,
                    inicio_iso=novo_inicio.replace(tzinfo=UTC).isoformat(),
                    fim_iso=novo_fim.replace(tzinfo=UTC).isoformat(),
                )
            except Exception as exc:
                falhas += 1
                detalhes.append(f"- Evento #{evento.id}: falha sync Google ({exc}).")
                continue

        sucesso += 1
        occupied.append((novo_inicio, novo_fim))

        cliente = db.query(Cliente).filter(Cliente.id == evento.cliente_id).first() if evento.cliente_id else None
        if cliente:
            chat_account, chat_conv = _latest_cliente_chat_route(db, cliente.id)
            if chat_account and chat_conv:
                try:
                    enviar_mensagens(
                        chat_account,
                        chat_conv,
                        [
                            "Sua consulta foi remarcada para a próxima semana no período da tarde, conforme ajuste de agenda. "
                            f"Novo horário: {novo_inicio.strftime('%d/%m %H:%M')}."
                        ],
                    )
                    notificadas += 1
                except Exception as exc:
                    detalhes.append(f"- Cliente {cliente.nome}: falha de notificação ({exc}).")
            else:
                detalhes.append(f"- Cliente {cliente.nome}: sem conversa ativa para notificação automática.")

        event = build_event_payload(
            queue_tipo="agenda_event_updated",
            tenant_id=nutri.tenant_id,
            nutricionista_id=nutri.id,
            cliente_id=evento.cliente_id,
            payload={"agenda_evento_id": evento.id, "google_event_id": evento.google_event_id},
        )
        publish_event("queue.agenda.sync", event)
        create_worker_job(
            db,
            event_id=event["event_id"],
            queue="queue.agenda.sync",
            tipo="agenda_event_updated",
            tenant_id=nutri.tenant_id,
            nutricionista_id=nutri.id,
            cliente_id=evento.cliente_id,
            payload=event,
        )

    db.commit()
    resumo = [
        "Remarcação em lote concluída.",
        f"- Consultas analisadas: {len(eventos)}",
        f"- Remarcadas com sucesso: {sucesso}",
        f"- Clientes notificadas no chat: {notificadas}",
        f"- Falhas/pedências: {falhas}",
        f"- Origem: {source_date}",
        f"- Destino: {target_date} ({target_period})",
    ]
    if detalhes:
        resumo.append("Detalhes:")
        resumo.extend(detalhes[:12])
    enviar_mensagens(account_id, conversation_id, ["\n".join(resumo)])


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


def _nutri_setup(db: Session, nutri: Nutricionista) -> dict:
    try:
        metadata = json.loads(nutri.permissoes or "{}")
        if isinstance(metadata, dict):
            setup = metadata.get("setup", {})
            return setup if isinstance(setup, dict) else {}
    except Exception:
        pass
    return {}


def _parse_work_window(setup: dict) -> tuple[int, int]:
    for key in ("disponibilidade_agenda", "periodo_trabalho"):
        value = str(setup.get(key) or "")
        m = re.search(r"(\d{1,2})[:h](\d{2}).*?(\d{1,2})[:h](\d{2})", value)
        if m:
            h1 = max(0, min(23, int(m.group(1))))
            h2 = max(0, min(23, int(m.group(3))))
            if h2 > h1:
                return h1, h2
    return 8, 19


def _duracao_consulta_minutos(setup: dict) -> int:
    raw = setup.get("duracao_consulta_minutos")
    try:
        val = int(raw)
        if 10 <= val <= 240:
            return val
    except Exception:
        pass
    return 60


def _resolve_source_day_for_availability(token: str, now_utc: datetime) -> datetime | None:
    rng = _parse_date_token(token, now_utc)
    if rng:
        return rng[0]
    return None


def _format_slots(day: datetime, slots: list[tuple[datetime, datetime]]) -> str:
    if not slots:
        return f"No dia {day.strftime('%d/%m/%Y')} não há janelas livres."
    lines = [f"Horários livres em {day.strftime('%d/%m/%Y')}: "]
    for s, e in slots[:20]:
        lines.append(f"- {s.strftime('%H:%M')} às {e.strftime('%H:%M')}")
    return "\n".join(lines)


def _horarios_livres_no_dia(db: Session, *, nutri: Nutricionista, day_token: str) -> str:
    now_utc = datetime.now(UTC).replace(tzinfo=None)
    day_start = _resolve_source_day_for_availability(day_token, now_utc)
    if not day_start:
        return "Não consegui identificar a data. Informe, por exemplo, 'amanhã', 'today' ou '2026-03-25'."
    day_end = day_start.replace(hour=23, minute=59, second=59, microsecond=999999)

    setup = _nutri_setup(db, nutri)
    start_hour, end_hour = _parse_work_window(setup)
    duracao_min = _duracao_consulta_minutos(setup)
    duration = timedelta(minutes=duracao_min)

    eventos = (
        db.query(AgendaEvento)
        .filter(
            AgendaEvento.nutricionista_id == nutri.id,
            AgendaEvento.status != "cancelado",
            AgendaEvento.inicio_em >= day_start,
            AgendaEvento.inicio_em <= day_end,
        )
        .order_by(AgendaEvento.inicio_em.asc())
        .all()
    )
    occupied = [(ev.inicio_em, ev.fim_em) for ev in eventos if ev.inicio_em and ev.fim_em]

    slot_start = day_start.replace(hour=start_hour, minute=0, second=0, microsecond=0)
    slot_end_limit = day_start.replace(hour=end_hour, minute=0, second=0, microsecond=0)
    step = timedelta(minutes=30)
    livres: list[tuple[datetime, datetime]] = []
    while slot_start + duration <= slot_end_limit:
        slot_end = slot_start + duration
        if all(not _is_overlap(slot_start, slot_end, b_start, b_end) for b_start, b_end in occupied):
            livres.append((slot_start, slot_end))
        slot_start += step
    return _format_slots(day_start, livres)


def _period_match(inicio: datetime, period: str) -> bool:
    p = (period or "").strip().lower()
    if not p:
        return True
    hour = inicio.hour
    if p == "morning":
        return 6 <= hour < 12
    if p == "afternoon":
        return 12 <= hour < 18
    if p == "evening":
        return 18 <= hour <= 23
    return True


def _listar_agenda_por_data(db: Session, *, nutri: Nutricionista, source_date: str, target_period: str = "") -> str:
    now_utc = datetime.now(UTC).replace(tzinfo=None)
    source_range = _parse_date_token(source_date, now_utc)
    if not source_range:
        return "Não consegui identificar a data/período da agenda. Informe por exemplo: hoje, amanhã, próxima semana ou YYYY-MM-DD."
    source_start, source_end = source_range

    eventos = (
        db.query(AgendaEvento)
        .filter(
            AgendaEvento.nutricionista_id == nutri.id,
            AgendaEvento.status != "cancelado",
            AgendaEvento.inicio_em >= source_start,
            AgendaEvento.inicio_em <= source_end,
        )
        .order_by(AgendaEvento.inicio_em.asc(), AgendaEvento.cliente_id.asc().nullslast())
        .all()
    )
    if target_period:
        eventos = [ev for ev in eventos if ev.inicio_em and _period_match(ev.inicio_em, target_period)]

    if not eventos:
        label = f"{source_date} ({target_period})" if target_period else source_date
        return f"Não há consultas agendadas para {label}."

    linhas = []
    header = f"Agenda {source_date}"
    if target_period:
        header += f" ({target_period})"
    linhas.append(header + ":")
    registros: list[tuple[datetime, str, str, str]] = []
    for ev in eventos:
        cliente_nome = "Sem cliente vinculado"
        if ev.cliente_id:
            cl = db.query(Cliente).filter(Cliente.id == ev.cliente_id).first()
            if cl and cl.nome:
                cliente_nome = cl.nome
        data_fmt = ev.inicio_em.strftime("%d/%m/%Y") if ev.inicio_em else "--/--/----"
        inicio_fmt = ev.inicio_em.strftime("%H:%M") if ev.inicio_em else "--:--"
        fim_fmt = ev.fim_em.strftime("%H:%M") if ev.fim_em else "--:--"
        dt_key = ev.inicio_em or datetime.max
        registros.append((dt_key, data_fmt, f"{inicio_fmt} às {fim_fmt}", cliente_nome))
    registros.sort(key=lambda item: (item[0], item[3].lower()))
    for _, data_fmt, hora_fmt, cliente_nome in registros:
        linhas.append(f"- Data: {data_fmt} | Hora: {hora_fmt} | Cliente: {cliente_nome}")
    return "\n".join(linhas)


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
    new_client_name = action_payload.get("new_client_name") or ""
    new_client_contact = action_payload.get("new_client_contact") or ""
    new_client_status = action_payload.get("new_client_status") or "potencial"
    cliente = _buscar_cliente_por_nome(db, nutri.id, client_name) if client_name else None

    if action == "send_meal_plan_copy":
        if not cliente:
            enviar_mensagens(account_id, conversation_id, ["Para enviar a cópia do plano, me confirme o nome da cliente no cadastro."])
            return
        _enviar_copia_plano_alimentar(db, nutri=nutri, account_id=account_id, conversation_id=conversation_id, cliente=cliente)
        return

    if action == "call_client":
        if not cliente:
            if new_client_name and new_client_contact:
                cliente, erro_cliente = _upsert_new_client(
                    db,
                    nutri=nutri,
                    nome=new_client_name,
                    contato=new_client_contact,
                    status_raw=new_client_status,
                )
                if erro_cliente or not cliente:
                    enviar_mensagens(account_id, conversation_id, [erro_cliente or "Falha ao cadastrar cliente."])
                    return
            else:
                enviar_mensagens(
                    account_id,
                    conversation_id,
                    [
                        "Não encontrei essa cliente no cadastro. Para contato com cliente novo, informe: "
                        "nome, contato (telefone/canal) e status (potencial, ativo, inativo ou satisfeito)."
                    ],
                )
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

    if action == "register_client":
        cliente_cadastrado, erro_cliente = _upsert_new_client(
            db,
            nutri=nutri,
            nome=new_client_name or client_name,
            contato=new_client_contact,
            status_raw=new_client_status,
        )
        if erro_cliente or not cliente_cadastrado:
            enviar_mensagens(
                account_id,
                conversation_id,
                [
                    erro_cliente
                    or "Não consegui cadastrar. Informe nome, contato e status (potencial, ativo, inativo ou satisfeito)."
                ],
            )
            return
        enviar_mensagens(
            account_id,
            conversation_id,
            [
                f"Cliente {cliente_cadastrado.nome} cadastrada com sucesso como {cliente_cadastrado.status}. "
                "Quando quiser, já posso iniciar o primeiro contato."
            ],
        )
        return

    if action == "register_and_contact_client":
        cliente_cadastrado, erro_cliente = _upsert_new_client(
            db,
            nutri=nutri,
            nome=new_client_name or client_name,
            contato=new_client_contact,
            status_raw=new_client_status,
        )
        if erro_cliente or not cliente_cadastrado:
            enviar_mensagens(
                account_id,
                conversation_id,
                [
                    erro_cliente
                    or "Não consegui cadastrar para contato. Informe nome, contato e status (potencial, ativo, inativo ou satisfeito)."
                ],
            )
            return
        objetivo = action_payload.get("objective") or "Primeiro contato para alinhar detalhes de consulta com a nutricionista."
        chamada = _enfileirar_ligacao(
            db,
            nutri=nutri,
            cliente=cliente_cadastrado,
            account_id=account_id,
            conversation_id=conversation_id,
            objetivo=objetivo,
        )
        if chamada:
            enviar_mensagens(
                account_id,
                conversation_id,
                [
                    f"Cliente {cliente_cadastrado.nome} cadastrada e contato iniciado. "
                    f"Ligação enfileirada (protocolo #{chamada.id})."
                ],
            )
            return
        enviar_mensagens(
            account_id,
            conversation_id,
            [
                f"Cliente {cliente_cadastrado.nome} cadastrada, mas não consegui iniciar contato automático. "
                "Verifique se o contato informado é um telefone válido."
            ],
        )
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

    if action == "list_schedule_by_date":
        source_date = action_payload.get("source_date") or "today"
        target_period = action_payload.get("target_period") or ""
        enviar_mensagens(
            account_id,
            conversation_id,
            [_listar_agenda_por_data(db, nutri=nutri, source_date=source_date, target_period=target_period)],
        )
        return

    if action == "check_day_availability":
        source_date = action_payload.get("source_date") or "today"
        resposta = _horarios_livres_no_dia(db, nutri=nutri, day_token=source_date)
        enviar_mensagens(account_id, conversation_id, [resposta])
        return

    if action == "bulk_reschedule_tomorrow_nextweek_afternoon":
        _remarcar_consultas_amanha_proxima_semana_tarde(
            db,
            nutri=nutri,
            account_id=account_id,
            conversation_id=conversation_id,
        )
        return

    if action == "reschedule_consultations":
        source_date = action_payload.get("source_date") or "tomorrow"
        target_date = action_payload.get("target_date") or "next_week"
        target_period = action_payload.get("target_period") or "afternoon"
        scope = action_payload.get("scope") or ("single_client" if cliente else "all_on_source_date")
        if scope == "single_client" and not cliente:
            enviar_mensagens(
                account_id,
                conversation_id,
                ["Para remarcação de uma cliente específica, confirme o nome exato da cliente."],
            )
            return
        _remarcar_consultas_amanha_proxima_semana_tarde(
            db,
            nutri=nutri,
            account_id=account_id,
            conversation_id=conversation_id,
            source_date=source_date,
            target_date=target_date,
            target_period=target_period,
            scope=scope,
            cliente_alvo=cliente,
        )
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

    if _is_admin_escalation_request(comando_raw):
        link = f"{FRONTEND_URL}/nutricionista/caixa-de-entrada?conversationId={conversation_id}"
        notificar_admins(
            f"[solicitacao-admin] A nutricionista {nutri.nome} (nutri_id={nutri.id}) pediu contato com admin. "
            f"account_id={account_id} conversation_id={conversation_id} link={link}"
        )
        enviar_mensagens(
            account_id,
            conversation_id,
            ["Encaminhei sua solicitação ao admin. Você receberá retorno por este canal em seguida."],
        )
        return

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
    decisao = _rule_based_decision_for_nutri(comando_raw) or _decidir_intencao_nutri(comando_raw, nutri.contexto_ia)
    decisao["original_message"] = comando_raw
    action = decisao.get("action", "unknown")
    confidence = float(decisao.get("confidence", 0) or 0)
    client_name = decisao.get("client_name") or ""
    new_client_name = (decisao.get("new_client_name") or "").strip()
    new_client_contact = (decisao.get("new_client_contact") or "").strip()
    new_client_status = (decisao.get("new_client_status") or "").strip()
    has_new_client_payload = bool((decisao.get("new_client_name") or "").strip() and (decisao.get("new_client_contact") or "").strip())
    cliente = _buscar_cliente_por_nome(db, nutri.id, client_name) if client_name else None

    if action in {"register_client", "register_and_contact_client"}:
        if not new_client_name or not new_client_contact or not new_client_status:
            enviar_mensagens(
                account_id,
                conversation_id,
                [
                    "Para cadastrar cliente novo, informe os dados básicos: nome, contato (telefone/canal) "
                    "e status (potencial, ativo, inativo ou satisfeito)."
                ],
            )
            return

    # 3) low-confidence nunca autoexecuta ação sensível
    if action in SENSITIVE_ACTIONS and (
        confidence < CONFIDENCE_THRESHOLD or (client_name and not cliente and not has_new_client_payload)
    ):
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
