import asyncio
import json
import os

os.environ["TEST_ENV"] = "1"

from starlette.requests import Request

from app.api.v1.chatwoot import receber_webhook_chatwoot
from app.db import SessionLocal, init_db
from app.domain.models.caixa_de_entrada import CaixaDeEntrada
from app.domain.models.chatwoot_account import ChatwootAccount
from app.domain.models.cliente import Cliente
from app.domain.models.conversa import Conversa
from app.domain.models.nutricionista import Nutricionista
from app.domain.models.tenant import Tenant
from app.domain.models.worker_job import WorkerJob


def _build_request(payload: dict) -> Request:
    body = json.dumps(payload).encode("utf-8")

    async def receive():
        return {"type": "http.request", "body": body, "more_body": False}

    scope = {
        "type": "http",
        "http_version": "1.1",
        "method": "POST",
        "scheme": "http",
        "path": "/api/v1/chatwoot/webhook",
        "raw_path": b"/api/v1/chatwoot/webhook",
        "query_string": b"",
        "headers": [(b"content-type", b"application/json")],
        "client": ("testclient", 50000),
        "server": ("testserver", 80),
    }
    return Request(scope, receive)


def _call_webhook(payload: dict, db: SessionLocal) -> dict:
    req = _build_request(payload)
    return asyncio.run(receber_webhook_chatwoot(req, db))


def setup_test_data():
    init_db()
    db = SessionLocal()
    db.query(WorkerJob).delete()
    db.query(Conversa).delete()
    db.query(Cliente).delete()
    db.query(CaixaDeEntrada).delete()
    db.query(ChatwootAccount).delete()
    db.query(Nutricionista).delete()
    db.query(Tenant).delete()
    db.commit()

    tenant = Tenant(nome="Tenant Teste", status="active", plano="pro")
    db.add(tenant)
    db.commit()
    db.refresh(tenant)

    nutri = Nutricionista(
        nome="Nutri Teste",
        email="nutri.teste@teste.com",
        password_hash="hash",
        plano="basic",
        status="active",
        tenant_id=tenant.id,
        tipo_user="nutri",
    )
    db.add(nutri)
    db.commit()
    db.refresh(nutri)

    conta = ChatwootAccount(
        tenant_id=tenant.id,
        nutricionista_id=nutri.id,
        chatwoot_account_id="cw-old-id",
        chatwoot_account_external_id="acct123",
        chatwoot_instance="cw-01",
        status="active",
        limite_inboxes_base=1,
        inboxes_extra=0,
    )
    db.add(conta)
    db.commit()

    caixa = CaixaDeEntrada(
        tipo="whatsapp",
        identificador_chatwoot="inbox-123",
        nutricionista_id=nutri.id,
    )
    db.add(caixa)
    db.commit()
    db.refresh(caixa)
    return db, nutri.id, caixa


def test_chatwoot_webhook_valido_enfileira_ia_e_salva_metadados():
    db, nutri_id, caixa = setup_test_data()
    payload = {
        "inbox_id": caixa.identificador_chatwoot,
        "conversation_id": "conv123",
        "account_id": "acct123",
        "sender": {"id": "chatwoot-contact-123"},
        "content": "Olá, gostaria de informações sobre planos",
    }
    response = _call_webhook(payload, db)
    assert response["status"] == "queued_ai"

    cliente = db.query(Cliente).filter(Cliente.contato_chatwoot == "chatwoot-contact-123").first()
    assert cliente is not None
    assert cliente.nutricionista_id == nutri_id

    conversa = db.query(Conversa).filter(Conversa.cliente_id == cliente.id).order_by(Conversa.id.desc()).first()
    assert conversa is not None
    assert conversa.chatwoot_account_id == "acct123"
    assert conversa.chatwoot_inbox_id == "inbox-123"
    assert conversa.canal_origem == "whatsapp"
    assert conversa.chatwoot_conversation_id == "conv123"

    job = db.query(WorkerJob).filter(WorkerJob.event_id == response["event_id"]).first()
    assert job is not None
    assert job.queue == "queue.atendimento"
    db.close()


def test_chatwoot_webhook_rejeita_account_sem_mapeamento():
    db, _, caixa = setup_test_data()
    payload = {
        "inbox_id": caixa.identificador_chatwoot,
        "conversation_id": "conv123",
        "account_id": "acct999",
        "sender": {"id": "chatwoot-contact-404"},
        "content": "Oi",
    }
    response = _call_webhook(payload, db)
    assert response["status"] == "account_unmapped"

    cliente = db.query(Cliente).filter(Cliente.contato_chatwoot == "chatwoot-contact-404").first()
    assert cliente is None
    db.close()

