from datetime import datetime
import os
import tempfile

import requests
from requests.auth import HTTPBasicAuth

from app.db import SessionLocal
from app.domain.models.voice_call import VoiceCall
from app.services.voice_history_service import persist_audio_from_local_file
from app.services.worker_job_service import update_worker_job_status
from app.workers.chatwoot_attachment_worker import enviar_arquivo_chatwoot
from app.workers.chatwoot_message_worker import enviar_mensagem_chatwoot
from app.workers.admin_monitor_worker import notificar_admins
from app.workers.redis_worker import set_if_not_exists

TWILIO_CALL_API_URL = os.getenv("TWILIO_CALL_API_URL")
TWILIO_API_TOKEN = os.getenv("TWILIO_API_TOKEN")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_FROM_NUMBER = os.getenv("TWILIO_FROM_NUMBER")
VOICE_TWIML_URL = os.getenv("VOICE_TWIML_URL")
VOICE_STATUS_CALLBACK_URL = os.getenv("VOICE_STATUS_CALLBACK_URL")
RETELL_WEBHOOK_URL = os.getenv("RETELL_WEBHOOK_URL")
RETELL_API_KEY = os.getenv("RETELL_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "EXAVITQu4vr4xnSDxMaL")
ELEVENLABS_MODEL_ID = os.getenv("ELEVENLABS_MODEL_ID", "eleven_multilingual_v2")


def _start_twilio_call(telefone_origem: str | None, telefone_destino: str) -> dict:
    if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN and TWILIO_FROM_NUMBER:
        url = (
            TWILIO_CALL_API_URL
            or f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_ACCOUNT_SID}/Calls.json"
        )
        response = requests.post(
            url,
            data={
                "From": telefone_origem or TWILIO_FROM_NUMBER,
                "To": telefone_destino,
                "Url": VOICE_TWIML_URL or "http://demo.twilio.com/docs/voice.xml",
                "StatusCallback": VOICE_STATUS_CALLBACK_URL or "",
                "StatusCallbackEvent": ["initiated", "ringing", "answered", "completed"],
            },
            auth=HTTPBasicAuth(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN),
            timeout=20,
        )
        response.raise_for_status()
        return response.json()

    if not TWILIO_CALL_API_URL or not TWILIO_API_TOKEN:
        return {"status": "mocked", "call_sid": f"mock-{datetime.utcnow().timestamp()}"}
    response = requests.post(
        TWILIO_CALL_API_URL,
        json={"from": telefone_origem, "to": telefone_destino},
        headers={"Authorization": f"Bearer {TWILIO_API_TOKEN}"},
        timeout=20,
    )
    response.raise_for_status()
    return response.json()


def _notify_retell(call_sid: str, voice_call_id: int) -> None:
    if not RETELL_WEBHOOK_URL or not RETELL_API_KEY:
        return
    requests.post(
        RETELL_WEBHOOK_URL,
        json={"call_sid": call_sid, "voice_call_id": voice_call_id},
        headers={"Authorization": f"Bearer {RETELL_API_KEY}"},
        timeout=20,
    )


def _sintetizar_audio_temporario(texto: str) -> str | None:
    if os.getenv("TEST_ENV", "0") == "1":
        fd, path = tempfile.mkstemp(suffix=".mp3", prefix="voice-msg-test-")
        with os.fdopen(fd, "wb") as f:
            f.write(b"mock-audio")
        return path

    if not ELEVENLABS_API_KEY:
        return None
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"
    response = requests.post(
        url,
        headers={
            "xi-api-key": ELEVENLABS_API_KEY,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
        },
        json={
            "model_id": ELEVENLABS_MODEL_ID,
            "text": texto,
        },
        timeout=30,
    )
    response.raise_for_status()
    fd, path = tempfile.mkstemp(suffix=".mp3", prefix="voice-msg-")
    with os.fdopen(fd, "wb") as f:
        f.write(response.content)
    return path


def _process_voice_message(event: dict):
    payload = event.get("payload", {})
    tenant_id = event.get("tenant_id")
    nutricionista_id = event.get("nutricionista_id")
    account_id = payload.get("account_id")
    conversation_id = payload.get("conversation_id")
    texto = (payload.get("text") or "").strip()
    cliente_id = payload.get("cliente_id")
    cliente_nome = payload.get("cliente_nome") or "cliente"

    if not account_id or not conversation_id or not texto:
        raise ValueError("voice_message_payload_invalid")

    local_path = None
    try:
        local_path = _sintetizar_audio_temporario(texto)
        if local_path:
            db = SessionLocal()
            try:
                if tenant_id and nutricionista_id:
                    persist_audio_from_local_file(
                        db,
                        tenant_id=int(tenant_id),
                        nutricionista_id=int(nutricionista_id),
                        cliente_id=int(cliente_id) if cliente_id is not None else None,
                        local_path=local_path,
                        original_filename=f"voice_message_{datetime.utcnow().timestamp()}.mp3",
                        nota_conversa="[VOICE_MESSAGE] Mensagem de voz gerada para envio no Chatwoot.",
                    )
            finally:
                db.close()
            enviado = enviar_arquivo_chatwoot(account_id, conversation_id, local_path)
            if enviado:
                enviar_mensagem_chatwoot(
                    account_id,
                    conversation_id,
                    f"Mensagem de voz enviada para {cliente_nome}.",
                )
                return
        enviar_mensagem_chatwoot(
            account_id,
            conversation_id,
            f"[Fallback texto] Mensagem de voz para {cliente_nome}: {texto}",
        )
    finally:
        if local_path and os.path.exists(local_path):
            try:
                os.remove(local_path)
            except Exception:
                pass


def process_voice_call(event: dict):
    event_id = event.get("event_id")
    if event_id and not set_if_not_exists(f"idempotency:{event_id}", "1", expire=3600):
        return

    db = SessionLocal()
    try:
        payload = event.get("payload", {})
        event_type = str(event.get("tipo") or "")
        if event_type == "voice_message_chatwoot":
            _process_voice_message(event)
            if event_id:
                update_worker_job_status(db, event_id=event_id, status="completed")
            return

        voice_call_id = payload.get("voice_call_id")
        if not voice_call_id:
            if event_id:
                update_worker_job_status(db, event_id=event_id, status="failed", erro="voice_call_id_missing")
            return
        voice_call = db.query(VoiceCall).filter(VoiceCall.id == voice_call_id).first()
        if not voice_call:
            if event_id:
                update_worker_job_status(db, event_id=event_id, status="failed", erro="voice_call_not_found")
            return

        result = _start_twilio_call(voice_call.telefone_origem, voice_call.telefone_destino)
        voice_call.twilio_call_sid = result.get("call_sid") or result.get("sid")
        voice_call.status = "dialing"
        voice_call.atualizado_em = datetime.utcnow()
        db.add(voice_call)
        db.commit()
        if voice_call.twilio_call_sid:
            _notify_retell(voice_call.twilio_call_sid, voice_call.id)

        if event_id:
            update_worker_job_status(db, event_id=event_id, status="completed")
    except Exception as exc:
        if event_id:
            update_worker_job_status(
                db,
                event_id=event_id,
                status="failed",
                tentativas_increment=True,
                erro=str(exc),
            )
        notificar_admins(f"Falha no worker de voz: {exc}")
    finally:
        db.close()
