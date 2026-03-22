import base64
from datetime import datetime
import hashlib
import hmac
import os
from urllib.parse import parse_qsl

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.v1.auth import get_current_user
from app.core.config import FRONTEND_URL
from app.db import get_db
from app.domain.models.cliente import Cliente
from app.domain.models.conversa import Conversa
from app.domain.models.nutricionista import Nutricionista
from app.domain.models.voice_call import VoiceCall
from app.services.ai_service import gerar_resposta_agente
from app.services.event_bus import build_event_payload, publish_event
from app.services.voice_history_service import persist_audio_from_url
from app.services.worker_job_service import create_worker_job
from app.workers.admin_monitor_worker import notificar_admins

router = APIRouter(prefix="/voz", tags=["Voz"])

TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_VALIDATE_SIGNATURE = os.getenv("TWILIO_VALIDATE_SIGNATURE", "0") == "1"
TWILIO_WEBHOOK_PUBLIC_URL = os.getenv("TWILIO_WEBHOOK_PUBLIC_URL")
VOICE_HANDOFF_STATUSES = {"failed", "busy", "no-answer", "canceled", "handoff_required", "human_required"}


class CriarChamadaRequest(BaseModel):
    telefone_destino: str = Field(min_length=8)
    cliente_id: int | None = None
    telefone_origem: str | None = None


class VoiceHandoffResponse(BaseModel):
    call_id: int
    cliente_id: int
    cliente_nome: str | None = None
    status: str
    motivo: str
    quando: str | None = None
    conversa_id: int | None = None
    conversa_link: str


def _twilio_signature_valid(signature: str | None, url: str, params: dict) -> bool:
    if not TWILIO_VALIDATE_SIGNATURE:
        return True
    if not signature or not TWILIO_AUTH_TOKEN:
        return False
    data = url
    for key in sorted(params.keys()):
        value = params.get(key)
        if value is None:
            continue
        data += f"{key}{value}"
    digest = hmac.new(TWILIO_AUTH_TOKEN.encode("utf-8"), data.encode("utf-8"), hashlib.sha1).digest()
    expected = base64.b64encode(digest).decode("utf-8")
    return hmac.compare_digest(expected, signature)


async def _request_payload(request: Request) -> dict:
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        return await request.json()

    if "application/x-www-form-urlencoded" in content_type or "multipart/form-data" in content_type:
        form = await request.form()
        return {k: v for k, v in form.items()}

    body = (await request.body()).decode("utf-8")
    if body:
        return dict(parse_qsl(body))
    return {}


def _registrar_handoff_conversa(db: Session, call: VoiceCall, motivo: str) -> int | None:
    if not call.cliente_id:
        return None
    ultima_conversa = (
        db.query(Conversa)
        .filter(Conversa.cliente_id == call.cliente_id)
        .order_by(Conversa.id.desc())
        .first()
    )
    caixa_id = ultima_conversa.caixa_id if ultima_conversa else None
    contexto_ia = ultima_conversa.contexto_ia if ultima_conversa else None

    conversa = Conversa(
        cliente_id=call.cliente_id,
        nutricionista_id=call.nutricionista_id,
        caixa_id=caixa_id,
        mensagem=f"[VOICE_FALLBACK] Handoff automático para humano. Motivo: {motivo}",
        modo="direto",
        contexto_ia=contexto_ia,
        em_conversa_direta=True,
    )
    db.add(conversa)
    db.commit()
    db.refresh(conversa)
    return conversa.id


def _fallback_humano(db: Session, call: VoiceCall, motivo: str) -> None:
    cliente = None
    if call.cliente_id:
        cliente = db.query(Cliente).filter(Cliente.id == call.cliente_id).first()
        if cliente:
            cliente.status = "em_atendimento_direto"
            db.add(cliente)
            db.commit()

    conversa_id = _registrar_handoff_conversa(db, call, motivo)
    if call.cliente_id and conversa_id:
        link = f"{FRONTEND_URL}/nutricionista/clientes/{call.cliente_id}/conversas/{conversa_id}"
    elif call.cliente_id:
        link = f"{FRONTEND_URL}/nutricionista/clientes/{call.cliente_id}"
    else:
        link = FRONTEND_URL
    mensagem = (
        f"[Fallback Voz] Chamada {call.id} entrou em fallback humano. "
        f"Motivo: {motivo}. "
        f"Cliente: {call.cliente_id or '-'} "
        f"Link: {link}"
    )
    notificar_admins(mensagem)


def _extrair_motivo_handoff(call: VoiceCall) -> str:
    if call.erro and call.erro.strip():
        return call.erro.strip()
    return f"status:{call.status}"


def _registrar_transcricao_conversa(db: Session, call: VoiceCall, texto: str, origem: str) -> None:
    if not call.cliente_id:
        return
    texto_limpo = (texto or "").strip()
    if not texto_limpo:
        return
    if len(texto_limpo) > 2000:
        texto_limpo = f"{texto_limpo[:2000]}..."
    conversa = Conversa(
        cliente_id=call.cliente_id,
        nutricionista_id=call.nutricionista_id,
        caixa_id=None,
        mensagem=f"[VOICE_TRANSCRIPT:{origem}] {texto_limpo}",
        modo="ia",
        em_conversa_direta=False,
        data=datetime.utcnow(),
    )
    db.add(conversa)
    db.commit()


@router.post("/chamadas", response_model=dict)
def criar_chamada(
    data: CriarChamadaRequest,
    db: Session = Depends(get_db),
    current_user: Nutricionista = Depends(get_current_user),
):
    chamada = VoiceCall(
        tenant_id=current_user.tenant_id,
        nutricionista_id=current_user.id,
        cliente_id=data.cliente_id,
        telefone_destino=data.telefone_destino,
        telefone_origem=data.telefone_origem,
        status="queued",
        criado_em=datetime.utcnow(),
        atualizado_em=datetime.utcnow(),
    )
    db.add(chamada)
    db.commit()
    db.refresh(chamada)

    event = build_event_payload(
        queue_tipo="voice_call_create",
        tenant_id=current_user.tenant_id,
        nutricionista_id=current_user.id,
        cliente_id=data.cliente_id,
        payload={
            "voice_call_id": chamada.id,
            "telefone_destino": data.telefone_destino,
            "telefone_origem": data.telefone_origem,
        },
    )
    publish_event("queue.voice.call", event)
    create_worker_job(
        db,
        event_id=event["event_id"],
        queue="queue.voice.call",
        tipo="voice_call_create",
        tenant_id=current_user.tenant_id,
        nutricionista_id=current_user.id,
        cliente_id=data.cliente_id,
        payload=event,
    )
    return {"status": "queued", "voice_call_id": chamada.id}


@router.get("/handoffs", response_model=list[VoiceHandoffResponse])
def listar_handoffs(
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: Nutricionista = Depends(get_current_user),
):
    if limit < 1:
        limit = 1
    if limit > 100:
        limit = 100

    query = db.query(VoiceCall).filter(VoiceCall.status.in_(VOICE_HANDOFF_STATUSES), VoiceCall.cliente_id.isnot(None))
    if current_user.papel != "admin":
        query = query.filter(VoiceCall.nutricionista_id == current_user.id, VoiceCall.tenant_id == current_user.tenant_id)

    calls = query.order_by(VoiceCall.atualizado_em.desc(), VoiceCall.id.desc()).limit(limit).all()
    resultados: list[VoiceHandoffResponse] = []
    for call in calls:
        cliente = db.query(Cliente).filter(Cliente.id == call.cliente_id).first() if call.cliente_id else None
        conversa = None
        if call.cliente_id:
            conversa = (
                db.query(Conversa)
                .filter(
                    Conversa.cliente_id == call.cliente_id,
                    Conversa.nutricionista_id == call.nutricionista_id,
                    Conversa.modo == "direto",
                )
                .order_by(Conversa.id.desc())
                .first()
            )
        conversa_id = conversa.id if conversa else None
        if call.cliente_id and conversa_id:
            conversa_link = f"/nutricionista/clientes/{call.cliente_id}/conversas/{conversa_id}"
        elif call.cliente_id:
            conversa_link = f"/nutricionista/clientes/{call.cliente_id}"
        else:
            conversa_link = "/nutricionista/clientes"

        resultados.append(
            VoiceHandoffResponse(
                call_id=call.id,
                cliente_id=call.cliente_id,
                cliente_nome=cliente.nome if cliente else None,
                status=call.status,
                motivo=_extrair_motivo_handoff(call),
                quando=(call.atualizado_em.isoformat() if call.atualizado_em else None),
                conversa_id=conversa_id,
                conversa_link=conversa_link,
            )
        )
    return resultados


@router.get("/chamadas/{call_id}", response_model=dict)
def obter_chamada(
    call_id: int,
    db: Session = Depends(get_db),
    current_user: Nutricionista = Depends(get_current_user),
):
    call = db.query(VoiceCall).filter(VoiceCall.id == call_id).first()
    if not call:
        raise HTTPException(status_code=404, detail="Chamada não encontrada")
    if current_user.papel != "admin" and call.nutricionista_id != current_user.id:
        raise HTTPException(status_code=403, detail="Acesso negado")
    return call.__dict__


@router.post("/twilio/webhook", response_model=dict)
async def twilio_webhook(
    request: Request,
    db: Session = Depends(get_db),
):
    payload = await _request_payload(request)
    signature = request.headers.get("X-Twilio-Signature")
    public_url = TWILIO_WEBHOOK_PUBLIC_URL or str(request.url)
    if not _twilio_signature_valid(signature, public_url, payload):
        raise HTTPException(status_code=401, detail="Assinatura Twilio inválida")

    call_sid = payload.get("CallSid")
    call_status = (payload.get("CallStatus") or "").lower()
    call_duration = payload.get("CallDuration")
    recording_url = payload.get("RecordingUrl")
    transcription_text = payload.get("TranscriptionText")

    call = db.query(VoiceCall).filter(VoiceCall.twilio_call_sid == call_sid).first()
    if not call:
        call = (
            db.query(VoiceCall)
            .filter(VoiceCall.status.in_(["queued", "dialing", "in_progress"]))
            .order_by(VoiceCall.id.desc())
            .first()
        )
    if not call:
        return {"status": "ignored", "reason": "call_not_found"}

    call.twilio_call_sid = call_sid or call.twilio_call_sid
    if call_status:
        call.status = call_status
    if call_duration is not None:
        try:
            call.duracao_segundos = int(call_duration)
        except Exception:
            pass
    if recording_url:
        call.recording_url = recording_url
        persist_audio_from_url(
            db,
            tenant_id=call.tenant_id,
            nutricionista_id=call.nutricionista_id,
            cliente_id=call.cliente_id,
            remote_url=recording_url,
            filename_hint=f"voice_call_{call.id}_twilio.mp3",
            nota_conversa="[VOICE_RECORDING] Gravação de ligação recebida via webhook Twilio.",
        )
    if transcription_text:
        call.transcricao = transcription_text
        _registrar_transcricao_conversa(db, call, transcription_text, "twilio")
        if not call.resumo:
            call.resumo = gerar_resposta_agente("consultor", f"Resuma a ligação em 5 linhas:\n{transcription_text}")
    call.atualizado_em = datetime.utcnow()
    db.add(call)
    db.commit()

    if call_status in {"busy", "failed", "no-answer", "canceled"}:
        _fallback_humano(db, call, f"twilio_status:{call_status}")

    return {"status": "ok", "voice_call_id": call.id}


@router.post("/retell/webhook", response_model=dict)
async def retell_webhook(
    request: Request,
    db: Session = Depends(get_db),
):
    payload = await _request_payload(request)
    voice_call_id = payload.get("voice_call_id")
    retell_call_id = payload.get("call_id") or payload.get("retell_call_id")
    twilio_call_sid = payload.get("twilio_call_sid")
    status = (payload.get("status") or "").lower()
    transcript = payload.get("transcript") or payload.get("transcription")
    summary = payload.get("summary")
    recording_url = payload.get("recording_url")

    call = None
    if voice_call_id:
        call = db.query(VoiceCall).filter(VoiceCall.id == int(voice_call_id)).first()
    if not call and twilio_call_sid:
        call = db.query(VoiceCall).filter(VoiceCall.twilio_call_sid == twilio_call_sid).first()
    if not call and retell_call_id:
        call = db.query(VoiceCall).filter(VoiceCall.retell_call_id == retell_call_id).first()
    if not call:
        return {"status": "ignored", "reason": "call_not_found"}

    if retell_call_id:
        call.retell_call_id = retell_call_id
    if status:
        call.status = status
    if transcript:
        call.transcricao = transcript
        _registrar_transcricao_conversa(db, call, transcript, "retell")
    if summary:
        call.resumo = summary
    elif transcript:
        call.resumo = gerar_resposta_agente("consultor", f"Resuma a ligação em 5 linhas:\n{transcript}")
    if recording_url:
        call.recording_url = recording_url
        persist_audio_from_url(
            db,
            tenant_id=call.tenant_id,
            nutricionista_id=call.nutricionista_id,
            cliente_id=call.cliente_id,
            remote_url=recording_url,
            filename_hint=f"voice_call_{call.id}_retell.mp3",
            nota_conversa="[VOICE_RECORDING] Gravação de ligação recebida via webhook Retell.",
        )
    call.atualizado_em = datetime.utcnow()
    db.add(call)
    db.commit()

    if status in {"failed", "handoff_required", "human_required"}:
        _fallback_humano(db, call, f"retell_status:{status}")

    return {"status": "ok", "voice_call_id": call.id}
