import asyncio
import json
import os

from starlette.requests import Request

from app.api.v1.auth import get_password_hash
from app.api.v1.voz import listar_handoffs, retell_webhook, twilio_webhook
from app.db import SessionLocal, init_db
from app.domain.models.cliente import Cliente
from app.domain.models.conversa import Conversa
from app.domain.models.nutricionista import Nutricionista
from app.domain.models.tenant import Tenant
from app.domain.models.voice_call import VoiceCall

os.environ["TEST_ENV"] = "1"


def _build_request(payload: dict) -> Request:
    body = json.dumps(payload).encode("utf-8")

    async def receive():
        return {"type": "http.request", "body": body, "more_body": False}

    scope = {
        "type": "http",
        "http_version": "1.1",
        "method": "POST",
        "scheme": "http",
        "path": "/api/v1/voz/webhook",
        "raw_path": b"/api/v1/voz/webhook",
        "query_string": b"",
        "headers": [(b"content-type", b"application/json")],
        "client": ("testclient", 50000),
        "server": ("testserver", 80),
    }
    return Request(scope, receive)


def _setup():
    init_db()
    db = SessionLocal()
    db.query(VoiceCall).delete()
    db.query(Conversa).delete()
    db.query(Cliente).delete()
    db.query(Nutricionista).delete()
    db.query(Tenant).delete()
    db.commit()

    tenant = Tenant(nome="Tenant Voz", status="active", plano="pro")
    db.add(tenant)
    db.commit()
    db.refresh(tenant)

    nutri = Nutricionista(
        nome="Nutri Voz",
        email="nutri.voz@test.com",
        password_hash=get_password_hash("senha123"),
        status="active",
        plano="pro",
        tenant_id=tenant.id,
        tipo_user="nutri",
    )
    db.add(nutri)
    db.commit()
    db.refresh(nutri)

    cliente = Cliente(
        nome="Cliente Voz",
        contato_chatwoot="cw-voz-1",
        status="cliente_ativo",
        nutricionista_id=nutri.id,
    )
    db.add(cliente)
    db.commit()
    db.refresh(cliente)

    call = VoiceCall(
        tenant_id=tenant.id,
        nutricionista_id=nutri.id,
        cliente_id=cliente.id,
        twilio_call_sid="CA123",
        telefone_destino="+551199999999",
        status="dialing",
    )
    db.add(call)
    db.commit()
    db.refresh(call)
    return db, cliente, call


def test_twilio_webhook_aplica_fallback_humano():
    db, cliente, call = _setup()
    payload = {"CallSid": "CA123", "CallStatus": "failed", "CallDuration": "0"}
    response = asyncio.run(twilio_webhook(_build_request(payload), db))
    assert response["status"] == "ok"

    db.refresh(call)
    db.refresh(cliente)
    assert call.status == "failed"
    assert cliente.status == "em_atendimento_direto"
    conversa = (
        db.query(Conversa)
        .filter(Conversa.cliente_id == cliente.id, Conversa.modo == "direto")
        .order_by(Conversa.id.desc())
        .first()
    )
    assert conversa is not None
    assert conversa.em_conversa_direta is True
    db.close()


def test_retell_webhook_persiste_resumo_e_transcricao():
    db, _, call = _setup()
    payload = {
        "voice_call_id": call.id,
        "call_id": "retell-1",
        "status": "completed",
        "transcript": "Paciente confirmou retorno na próxima semana.",
        "summary": "Ligação concluída com confirmação de retorno.",
    }
    response = asyncio.run(retell_webhook(_build_request(payload), db))
    assert response["status"] == "ok"

    db.refresh(call)
    assert call.retell_call_id == "retell-1"
    assert call.status == "completed"
    assert "Paciente confirmou" in (call.transcricao or "")
    assert "Ligação concluída" in (call.resumo or "")
    db.close()


def test_listar_handoffs_retorna_somente_da_nutri():
    db, cliente, call = _setup()
    payload = {"CallSid": "CA123", "CallStatus": "failed", "CallDuration": "0"}
    asyncio.run(twilio_webhook(_build_request(payload), db))

    other_tenant = Tenant(nome="Outro Tenant", status="active", plano="pro")
    db.add(other_tenant)
    db.commit()
    db.refresh(other_tenant)

    other_nutri = Nutricionista(
        nome="Outra Nutri",
        email="outra.nutri@test.com",
        password_hash=get_password_hash("senha123"),
        status="active",
        plano="pro",
        tenant_id=other_tenant.id,
        tipo_user="nutri",
    )
    db.add(other_nutri)
    db.commit()
    db.refresh(other_nutri)

    other_cliente = Cliente(
        nome="Cliente Externo",
        contato_chatwoot="cw-externo",
        status="cliente_ativo",
        nutricionista_id=other_nutri.id,
    )
    db.add(other_cliente)
    db.commit()
    db.refresh(other_cliente)

    other_call = VoiceCall(
        tenant_id=other_tenant.id,
        nutricionista_id=other_nutri.id,
        cliente_id=other_cliente.id,
        twilio_call_sid="CA999",
        telefone_destino="+551188888888",
        status="failed",
    )
    db.add(other_call)
    db.commit()

    handoffs = listar_handoffs(20, db, db.query(Nutricionista).filter(Nutricionista.id == call.nutricionista_id).first())
    assert len(handoffs) >= 1
    assert all(item.cliente_id != other_cliente.id for item in handoffs)
    assert any(item.cliente_id == cliente.id for item in handoffs)
    db.close()
