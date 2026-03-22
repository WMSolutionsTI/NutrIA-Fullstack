from datetime import UTC, datetime, timedelta
import json

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.v1.auth import get_current_user
from app.api.v1.integracoes_google import get_valid_google_access_token
from app.db import get_db
from app.domain.models.agenda_evento import AgendaEvento
from app.domain.models.google_calendar_integration import GoogleCalendarIntegration
from app.domain.models.nutricionista import Nutricionista
from app.domain.models.pagamento import Pagamento
from app.services.anamnese_service import ensure_anamnese_workflow_for_cliente
from app.services.event_bus import build_event_payload, publish_event
from app.services.google_calendar_service import (
    create_google_event,
    delete_google_event,
    list_busy_slots,
    update_google_event,
)
from app.services.worker_job_service import create_worker_job

router = APIRouter(prefix="/agenda", tags=["Agenda"])


class AgendaEventoCreateRequest(BaseModel):
    titulo: str = Field(min_length=3)
    descricao: str | None = None
    inicio_em: datetime
    fim_em: datetime
    cliente_id: int | None = None
    modalidade: str | None = None


class AgendaEventoUpdateRequest(BaseModel):
    titulo: str | None = None
    descricao: str | None = None
    inicio_em: datetime | None = None
    fim_em: datetime | None = None
    status: str | None = None
    modalidade: str | None = None


def _get_google_integration_or_400(db: Session, nutri_id: int) -> GoogleCalendarIntegration:
    integration = (
        db.query(GoogleCalendarIntegration)
        .filter(
            GoogleCalendarIntegration.nutricionista_id == nutri_id,
            GoogleCalendarIntegration.status == "active",
        )
        .first()
    )
    if not integration:
        raise HTTPException(status_code=400, detail="Google Agenda não conectada")
    return integration


def _utc_iso(dt: datetime) -> str:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=UTC).isoformat()
    return dt.astimezone(UTC).isoformat()


def _load_setup(current_user: Nutricionista) -> dict:
    if not current_user.permissoes:
        return {}
    try:
        parsed = json.loads(current_user.permissoes)
    except Exception:
        return {}
    if not isinstance(parsed, dict):
        return {}
    setup = parsed.get("setup")
    return setup if isinstance(setup, dict) else {}


def _allowed_modalidades(current_user: Nutricionista) -> set[str]:
    setup = _load_setup(current_user)
    raw = str(setup.get("metodo_atendimento") or "").lower()
    if not raw:
        return set()
    has_online = "online" in raw
    has_presencial = "presencial" in raw
    if has_online and has_presencial:
        return {"online", "presencial"}
    if has_online:
        return {"online"}
    if has_presencial:
        return {"presencial"}
    return set()


def _resolve_modalidade(modalidade: str | None, current_user: Nutricionista) -> str | None:
    allowed = _allowed_modalidades(current_user)
    normalized = (modalidade or "").strip().lower()
    if normalized and normalized not in {"online", "presencial"}:
        raise HTTPException(status_code=400, detail="Modalidade inválida. Use 'online' ou 'presencial'.")
    if not allowed:
        return normalized or None
    if normalized:
        if normalized not in allowed:
            raise HTTPException(status_code=400, detail="Modalidade não permitida para esta nutricionista.")
        return normalized
    if len(allowed) == 1:
        return next(iter(allowed))
    raise HTTPException(
        status_code=400,
        detail="Informe a modalidade da consulta (online/presencial) conforme perfil da nutricionista.",
    )


def _try_start_anamnese_if_billing_exists(
    db: Session,
    *,
    evento: AgendaEvento,
    current_user: Nutricionista,
) -> None:
    if not evento.cliente_id:
        return
    cobranca = (
        db.query(Pagamento)
        .filter(
            Pagamento.cliente_id == evento.cliente_id,
            Pagamento.nutricionista_id == current_user.id,
            Pagamento.status.in_(["pendente", "pago"]),
        )
        .order_by(Pagamento.id.desc())
        .first()
    )
    if not cobranca:
        return
    ensure_anamnese_workflow_for_cliente(
        db,
        cliente_id=evento.cliente_id,
        nutricionista_id=current_user.id,
        tenant_id=current_user.tenant_id,
        pagamento_id=cobranca.id,
        origin="agenda_event",
    )


@router.get("/eventos", response_model=list)
def listar_eventos(
    db: Session = Depends(get_db),
    current_user: Nutricionista = Depends(get_current_user),
):
    eventos = (
        db.query(AgendaEvento)
        .filter(
            AgendaEvento.nutricionista_id == current_user.id,
            AgendaEvento.status != "deleted",
        )
        .order_by(AgendaEvento.inicio_em.asc())
        .all()
    )
    return eventos


@router.get("/eventos/{evento_id}", response_model=dict)
def obter_evento(
    evento_id: int,
    db: Session = Depends(get_db),
    current_user: Nutricionista = Depends(get_current_user),
):
    evento = db.query(AgendaEvento).filter(AgendaEvento.id == evento_id).first()
    if not evento:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    if evento.nutricionista_id != current_user.id:
        raise HTTPException(status_code=403, detail="Acesso negado")
    return evento.__dict__


@router.get("/disponibilidade", response_model=dict)
def disponibilidade_agenda(
    dias: int = 7,
    db: Session = Depends(get_db),
    current_user: Nutricionista = Depends(get_current_user),
):
    integration = _get_google_integration_or_400(db, current_user.id)
    access_token = get_valid_google_access_token(db, integration)
    inicio = datetime.now(UTC)
    fim = inicio + timedelta(days=min(max(dias, 1), 30))
    slots = list_busy_slots(
        access_token,
        calendar_id=integration.calendar_id or "primary",
        time_min_iso=inicio.isoformat(),
        time_max_iso=fim.isoformat(),
    )
    return {"dias_consultados": dias, "ocupados": slots}


@router.post("/eventos", response_model=dict)
def criar_evento(
    data: AgendaEventoCreateRequest,
    db: Session = Depends(get_db),
    current_user: Nutricionista = Depends(get_current_user),
):
    if data.fim_em <= data.inicio_em:
        raise HTTPException(status_code=400, detail="Período inválido: fim deve ser após início")
    modalidade = _resolve_modalidade(data.modalidade, current_user)

    integration = _get_google_integration_or_400(db, current_user.id)
    access_token = get_valid_google_access_token(db, integration)
    google_event = create_google_event(
        access_token,
        calendar_id=integration.calendar_id or "primary",
        titulo=data.titulo,
        descricao=data.descricao,
        inicio_iso=_utc_iso(data.inicio_em),
        fim_iso=_utc_iso(data.fim_em),
    )

    evento = AgendaEvento(
        tenant_id=current_user.tenant_id,
        nutricionista_id=current_user.id,
        cliente_id=data.cliente_id,
        titulo=data.titulo,
        descricao=data.descricao,
        inicio_em=data.inicio_em,
        fim_em=data.fim_em,
        status="agendado",
        modalidade=modalidade,
        google_event_id=google_event.get("id"),
        origem="painel",
        criado_em=datetime.utcnow(),
        atualizado_em=datetime.utcnow(),
    )
    db.add(evento)
    db.commit()
    db.refresh(evento)

    event = build_event_payload(
        queue_tipo="agenda_event_created",
        tenant_id=current_user.tenant_id,
        nutricionista_id=current_user.id,
        cliente_id=data.cliente_id,
        payload={"agenda_evento_id": evento.id, "google_event_id": evento.google_event_id},
    )
    publish_event("queue.agenda.sync", event)
    create_worker_job(
        db,
        event_id=event["event_id"],
        queue="queue.agenda.sync",
        tipo="agenda_event_created",
        tenant_id=current_user.tenant_id,
        nutricionista_id=current_user.id,
        cliente_id=data.cliente_id,
        payload=event,
    )
    _try_start_anamnese_if_billing_exists(db, evento=evento, current_user=current_user)
    return {"status": "agendado", "evento_id": evento.id, "google_event_id": evento.google_event_id}


@router.patch("/eventos/{evento_id}", response_model=dict)
def atualizar_evento(
    evento_id: int,
    data: AgendaEventoUpdateRequest,
    db: Session = Depends(get_db),
    current_user: Nutricionista = Depends(get_current_user),
):
    evento = db.query(AgendaEvento).filter(AgendaEvento.id == evento_id).first()
    if not evento:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    if evento.nutricionista_id != current_user.id:
        raise HTTPException(status_code=403, detail="Acesso negado")

    integration = _get_google_integration_or_400(db, current_user.id)
    modalidade = _resolve_modalidade(data.modalidade, current_user) if data.modalidade is not None else evento.modalidade
    access_token = get_valid_google_access_token(db, integration)

    evento.titulo = data.titulo or evento.titulo
    evento.descricao = data.descricao if data.descricao is not None else evento.descricao
    evento.inicio_em = data.inicio_em or evento.inicio_em
    evento.fim_em = data.fim_em or evento.fim_em
    evento.status = data.status or evento.status
    evento.modalidade = modalidade
    evento.atualizado_em = datetime.utcnow()

    if evento.google_event_id:
        update_google_event(
            access_token,
            calendar_id=integration.calendar_id or "primary",
            google_event_id=evento.google_event_id,
            titulo=evento.titulo,
            descricao=evento.descricao,
            inicio_iso=_utc_iso(evento.inicio_em),
            fim_iso=_utc_iso(evento.fim_em),
        )

    db.add(evento)
    db.commit()
    db.refresh(evento)
    event = build_event_payload(
        queue_tipo="agenda_event_updated",
        tenant_id=current_user.tenant_id,
        nutricionista_id=current_user.id,
        cliente_id=evento.cliente_id,
        payload={"agenda_evento_id": evento.id, "google_event_id": evento.google_event_id},
    )
    publish_event("queue.agenda.sync", event)
    create_worker_job(
        db,
        event_id=event["event_id"],
        queue="queue.agenda.sync",
        tipo="agenda_event_updated",
        tenant_id=current_user.tenant_id,
        nutricionista_id=current_user.id,
        cliente_id=evento.cliente_id,
        payload=event,
    )
    _try_start_anamnese_if_billing_exists(db, evento=evento, current_user=current_user)
    return {"status": "atualizado", "evento_id": evento.id}


@router.delete("/eventos/{evento_id}", response_model=dict)
def cancelar_evento(
    evento_id: int,
    db: Session = Depends(get_db),
    current_user: Nutricionista = Depends(get_current_user),
):
    evento = db.query(AgendaEvento).filter(AgendaEvento.id == evento_id).first()
    if not evento:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    if evento.nutricionista_id != current_user.id:
        raise HTTPException(status_code=403, detail="Acesso negado")

    integration = _get_google_integration_or_400(db, current_user.id)
    access_token = get_valid_google_access_token(db, integration)
    if evento.google_event_id:
        delete_google_event(
            access_token,
            calendar_id=integration.calendar_id or "primary",
            google_event_id=evento.google_event_id,
        )

    evento.status = "cancelado"
    evento.atualizado_em = datetime.utcnow()
    db.add(evento)
    db.commit()
    event = build_event_payload(
        queue_tipo="agenda_event_deleted",
        tenant_id=current_user.tenant_id,
        nutricionista_id=current_user.id,
        cliente_id=evento.cliente_id,
        payload={"agenda_evento_id": evento.id, "google_event_id": evento.google_event_id},
    )
    publish_event("queue.agenda.sync", event)
    create_worker_job(
        db,
        event_id=event["event_id"],
        queue="queue.agenda.sync",
        tipo="agenda_event_deleted",
        tenant_id=current_user.tenant_id,
        nutricionista_id=current_user.id,
        cliente_id=evento.cliente_id,
        payload=event,
    )
    return {"status": "cancelado", "evento_id": evento.id}
