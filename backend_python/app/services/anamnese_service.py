from __future__ import annotations

from datetime import UTC, datetime, timedelta
import json
import re

from sqlalchemy.orm import Session

from app.domain.models.agenda_evento import AgendaEvento
from app.domain.models.anamnese_workflow import AnamneseWorkflow
from app.domain.models.cliente import Cliente
from app.domain.models.conversa import Conversa
from app.domain.models.nutricionista import Nutricionista
from app.domain.models.pagamento import Pagamento
from app.services.ai_service import gerar_resposta_agente
from app.utils.text_normalize import normalize_pt_text

ANAMNESE_REQUIRED_FIELDS = [
    "objetivo",
    "historico_clinico",
    "medicamentos",
    "alergias_restricoes",
    "rotina_alimentar",
    "hidratacao",
    "sono",
    "atividade_fisica",
    "dados_antropometricos",
    "fotos_refeicoes",
]


def _send_messages(account_id: str, conversation_id: str, messages: list[str]) -> None:
    from app.workers.quebrar_enviar_mensagens_worker import enviar_mensagens

    enviar_mensagens(account_id, conversation_id, messages)


def _as_json_dict(raw: str | None) -> dict:
    if not raw:
        return {}
    try:
        parsed = json.loads(raw)
        return parsed if isinstance(parsed, dict) else {}
    except Exception:
        return {}


def _as_json_list(raw: str | None) -> list[str]:
    if not raw:
        return []
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, list):
            return [str(item) for item in parsed if str(item).strip()]
    except Exception:
        pass
    return []


def _dump_json(value: dict | list[str]) -> str:
    return json.dumps(value, ensure_ascii=False)


def _extract_json(text: str) -> dict:
    if not text:
        return {}
    try:
        payload = json.loads(text)
        return payload if isinstance(payload, dict) else {}
    except Exception:
        pass
    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if not match:
        return {}
    try:
        payload = json.loads(match.group(0))
        return payload if isinstance(payload, dict) else {}
    except Exception:
        return {}


def _latest_chat_route(db: Session, cliente_id: int) -> tuple[str | None, str | None]:
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


def _find_next_agendamento(db: Session, cliente_id: int, nutri_id: int) -> AgendaEvento | None:
    now = datetime.now(UTC).replace(tzinfo=None)
    return (
        db.query(AgendaEvento)
        .filter(
            AgendaEvento.cliente_id == cliente_id,
            AgendaEvento.nutricionista_id == nutri_id,
            AgendaEvento.status == "agendado",
            AgendaEvento.inicio_em > now,
        )
        .order_by(AgendaEvento.inicio_em.asc())
        .first()
    )


def _pending_fields(data: dict) -> list[str]:
    missing = []
    for key in ANAMNESE_REQUIRED_FIELDS:
        value = data.get(key)
        if not value or (isinstance(value, str) and not value.strip()):
            missing.append(key)
    return missing


def _human_pending_items(items: list[str]) -> str:
    labels = {
        "objetivo": "objetivo principal do acompanhamento",
        "historico_clinico": "histórico clínico relevante",
        "medicamentos": "medicamentos em uso",
        "alergias_restricoes": "alergias/intolerâncias/restrições",
        "rotina_alimentar": "rotina alimentar atual",
        "hidratacao": "hidratação média diária",
        "sono": "rotina de sono",
        "atividade_fisica": "atividade física semanal",
        "dados_antropometricos": "peso/altura e medidas disponíveis",
        "fotos_refeicoes": "fotos recentes das refeições",
    }
    readable = [labels.get(item, item) for item in items]
    return ", ".join(readable)


def _heuristic_extract(message: str) -> dict:
    text = normalize_pt_text(message)
    data: dict[str, str] = {}
    if any(k in text for k in {"objetivo", "meta", "emagrecer", "ganhar massa", "saude"}):
        data["objetivo"] = message
    if any(k in text for k in {"diabetes", "hipertens", "cirurgia", "doenca", "problema de saude"}):
        data["historico_clinico"] = message
    if any(k in text for k in {"medicamento", "remedio", "remedio", "tarja"}):
        data["medicamentos"] = message
    if any(k in text for k in {"alergia", "intolerancia", "restricao"}):
        data["alergias_restricoes"] = message
    if any(k in text for k in {"cafe", "almoco", "jantar", "lanche", "alimentacao"}):
        data["rotina_alimentar"] = message
    if any(k in text for k in {"agua", "litro", "hidrata"}):
        data["hidratacao"] = message
    if any(k in text for k in {"sono", "durmo", "acordo", "insonia"}):
        data["sono"] = message
    if any(k in text for k in {"academia", "treino", "corrida", "caminhada", "atividade fisica"}):
        data["atividade_fisica"] = message
    if any(k in text for k in {"peso", "altura", "imc", "kg", "cm"}):
        data["dados_antropometricos"] = message
    if any(k in text for k in {"foto", "imagem", "anexo"}):
        data["fotos_refeicoes"] = "informado"
    return data


def _ai_extract(message: str, current_data: dict) -> dict:
    prompt = f"""
Extraia dados de anamnese nutricional da mensagem abaixo.
Responda SOMENTE JSON válido no formato:
{{
  "dados": {{
    "objetivo": "",
    "historico_clinico": "",
    "medicamentos": "",
    "alergias_restricoes": "",
    "rotina_alimentar": "",
    "hidratacao": "",
    "sono": "",
    "atividade_fisica": "",
    "dados_antropometricos": "",
    "fotos_refeicoes": ""
  }}
}}

Dados já coletados:
{json.dumps(current_data, ensure_ascii=False)}

Mensagem:
{message}
"""
    raw = gerar_resposta_agente(
        "especialista_anamnese",
        prompt,
        contexto="Extração estruturada de anamnese em português.",
        model="gpt-4o-mini",
        temperature=0.1,
    )
    parsed = _extract_json(raw)
    data = parsed.get("dados") if isinstance(parsed, dict) else {}
    return data if isinstance(data, dict) else {}


def _build_intro_message(cliente_nome: str, consulta_em: datetime, pendentes: list[str]) -> str:
    limite = consulta_em - timedelta(days=1)
    prazo = limite.strftime("%d/%m %H:%M")
    return (
        f"Olá {cliente_nome}! Vamos iniciar sua anamnese pré-consulta para personalizar seu atendimento.\n"
        f"Preciso concluir essa coleta até {prazo} (um dia antes da consulta).\n"
        f"Itens pendentes agora: {_human_pending_items(pendentes)}.\n"
        "Pode responder aos poucos e também enviar fotos quando necessário."
    )


def ensure_anamnese_workflow_for_cliente(
    db: Session,
    *,
    cliente_id: int,
    nutricionista_id: int,
    tenant_id: int,
    pagamento_id: int | None = None,
    origin: str = "system",
) -> AnamneseWorkflow | None:
    evento = _find_next_agendamento(db, cliente_id=cliente_id, nutri_id=nutricionista_id)
    if not evento:
        return None

    prazo = evento.inicio_em - timedelta(days=1)
    if prazo <= datetime.now(UTC).replace(tzinfo=None):
        prazo = evento.inicio_em - timedelta(hours=2)

    workflow = (
        db.query(AnamneseWorkflow)
        .filter(
            AnamneseWorkflow.cliente_id == cliente_id,
            AnamneseWorkflow.agenda_evento_id == evento.id,
            AnamneseWorkflow.status.in_(["pending", "in_progress", "overdue"]),
        )
        .order_by(AnamneseWorkflow.id.desc())
        .first()
    )
    if workflow:
        workflow.prazo_conclusao_em = prazo
        workflow.atualizado_em = datetime.utcnow()
        if pagamento_id:
            workflow.pagamento_id = pagamento_id
        db.add(workflow)
        db.commit()
        db.refresh(workflow)
        return workflow

    initial_data: dict = {}
    pending = _pending_fields(initial_data)
    workflow = AnamneseWorkflow(
        tenant_id=tenant_id,
        nutricionista_id=nutricionista_id,
        cliente_id=cliente_id,
        agenda_evento_id=evento.id,
        pagamento_id=pagamento_id,
        status="pending",
        dados_coletados=_dump_json(initial_data),
        itens_pendentes=_dump_json(pending),
        ultimo_followup_em=None,
        proximo_followup_em=datetime.utcnow(),
        prazo_conclusao_em=prazo,
        criado_em=datetime.utcnow(),
        atualizado_em=datetime.utcnow(),
    )
    db.add(workflow)
    db.commit()
    db.refresh(workflow)

    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if cliente:
        account_id, conversation_id = _latest_chat_route(db, cliente.id)
        if account_id and conversation_id:
            _send_messages(
                account_id,
                conversation_id,
                [_build_intro_message(cliente.nome, evento.inicio_em, pending)],
            )

    from app.services.event_bus import build_event_payload, publish_event
    from app.services.worker_job_service import create_worker_job

    event = build_event_payload(
        queue_tipo="anamnese_followup_tick",
        tenant_id=tenant_id,
        nutricionista_id=nutricionista_id,
        cliente_id=cliente_id,
        payload={
            "tipo": "anamnese_followup_tick",
            "anamnese_workflow_id": workflow.id,
            "origin": origin,
        },
    )
    publish_event("queue.notifications", event)
    create_worker_job(
        db,
        event_id=event["event_id"],
        queue="queue.notifications",
        tipo="anamnese_followup_tick",
        tenant_id=tenant_id,
        nutricionista_id=nutricionista_id,
        cliente_id=cliente_id,
        payload=event,
    )
    return workflow


def process_anamnese_message(
    db: Session,
    *,
    cliente: Cliente,
    nutri: Nutricionista,
    message: str,
) -> tuple[bool, str | None]:
    workflow = (
        db.query(AnamneseWorkflow)
        .filter(
            AnamneseWorkflow.cliente_id == cliente.id,
            AnamneseWorkflow.nutricionista_id == nutri.id,
            AnamneseWorkflow.status.in_(["pending", "in_progress", "overdue"]),
        )
        .order_by(AnamneseWorkflow.id.desc())
        .first()
    )
    if not workflow:
        return False, None

    now = datetime.utcnow()
    current_data = _as_json_dict(workflow.dados_coletados)
    extracted = _heuristic_extract(message)
    ai_data = _ai_extract(message, current_data)
    for key, value in ai_data.items():
        if isinstance(value, str) and value.strip():
            extracted[key] = value.strip()
    if not extracted:
        # continua a coleta sem marcar nada novo
        pending = _as_json_list(workflow.itens_pendentes) or ANAMNESE_REQUIRED_FIELDS
        reply = (
            "Perfeito, seguimos com a anamnese em etapas. "
            f"Ainda preciso de: {_human_pending_items(pending[:3])}."
        )
        return True, reply

    current_data.update(extracted)
    pending = _pending_fields(current_data)
    workflow.dados_coletados = _dump_json(current_data)
    workflow.itens_pendentes = _dump_json(pending)
    workflow.atualizado_em = now
    workflow.ultimo_followup_em = now
    workflow.proximo_followup_em = now + timedelta(hours=8)

    if not pending:
        workflow.status = "completed"
        workflow.concluido_em = now
        db.add(workflow)
        db.commit()
        return (
            True,
            "Anamnese inicial concluída com sucesso. Obrigada pelas informações! "
            "Se houver atualização antes da consulta, pode me chamar aqui.",
        )

    workflow.status = "in_progress"
    db.add(workflow)
    db.commit()
    return (
        True,
        "Recebi e registrei suas informações. "
        f"Para avançar, ainda faltam: {_human_pending_items(pending[:4])}.",
    )


def send_anamnese_followup_tick(db: Session, payload: dict) -> dict:
    now = datetime.utcnow()
    workflow_id = payload.get("anamnese_workflow_id")
    q = db.query(AnamneseWorkflow).filter(AnamneseWorkflow.status.in_(["pending", "in_progress", "overdue"]))
    if workflow_id:
        q = q.filter(AnamneseWorkflow.id == int(workflow_id))

    workflows = q.all()
    sent = 0
    for workflow in workflows:
        if workflow.proximo_followup_em and workflow.proximo_followup_em > now:
            continue
        cliente = db.query(Cliente).filter(Cliente.id == workflow.cliente_id).first()
        if not cliente:
            continue
        evento = db.query(AgendaEvento).filter(AgendaEvento.id == workflow.agenda_evento_id).first()
        if not evento or evento.status != "agendado":
            workflow.status = "cancelled"
            workflow.atualizado_em = now
            db.add(workflow)
            db.commit()
            continue

        pending = _as_json_list(workflow.itens_pendentes)
        if not pending:
            workflow.status = "completed"
            workflow.concluido_em = now
            db.add(workflow)
            db.commit()
            continue

        account_id, conversation_id = _latest_chat_route(db, cliente.id)
        if not account_id or not conversation_id:
            continue

        deadline = workflow.prazo_conclusao_em or (evento.inicio_em - timedelta(days=1))
        if now > deadline:
            workflow.status = "overdue"
            msg = (
                "Estamos com a anamnese pendente e sua consulta está próxima. "
                f"Envie hoje, por favor: {_human_pending_items(pending[:4])}."
            )
            next_hours = 3
        else:
            msg = (
                "Lembrete de pré-consulta: seguimos com sua anamnese em andamento. "
                f"Pendências atuais: {_human_pending_items(pending[:4])}."
            )
            next_hours = 8 if (deadline - now) > timedelta(days=1) else 4

        _send_messages(account_id, conversation_id, [msg])
        workflow.ultimo_followup_em = now
        workflow.proximo_followup_em = now + timedelta(hours=next_hours)
        workflow.atualizado_em = now
        db.add(workflow)
        db.commit()
        sent += 1

    return {"status": "ok", "sent": sent}


def handle_payment_confirmed_for_anamnese(db: Session, pagamento: Pagamento) -> AnamneseWorkflow | None:
    nutri_id = pagamento.nutricionista_id
    cliente_id = pagamento.cliente_id
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    nutri = db.query(Nutricionista).filter(Nutricionista.id == nutri_id).first()
    if not cliente or not nutri:
        return None
    return ensure_anamnese_workflow_for_cliente(
        db,
        cliente_id=cliente_id,
        nutricionista_id=nutri_id,
        tenant_id=nutri.tenant_id,
        pagamento_id=pagamento.id,
        origin="payment_confirmed",
    )
