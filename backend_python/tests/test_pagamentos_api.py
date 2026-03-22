import asyncio
import json
import os
from datetime import UTC, datetime, timedelta

os.environ["TEST_ENV"] = "1"

from starlette.requests import Request

from app.api.v1.pagamentos import asaas_webhook
from app.db import SessionLocal, init_db
from app.domain.models.agenda_evento import AgendaEvento
from app.domain.models.anamnese_workflow import AnamneseWorkflow
from app.domain.models.chatwoot_account import ChatwootAccount
from app.domain.models.cliente import Cliente
from app.domain.models.contabilidade import Contabilidade
from app.domain.models.nutricionista import Nutricionista
from app.domain.models.pagamento import Pagamento
from app.domain.models.saas_signup_request import SaasSignupRequest
from app.domain.models.tenant import Tenant


def _build_request(payload: dict) -> Request:
    body = json.dumps(payload).encode("utf-8")

    async def receive():
        return {"type": "http.request", "body": body, "more_body": False}

    scope = {
        "type": "http",
        "http_version": "1.1",
        "method": "POST",
        "scheme": "http",
        "path": "/api/v1/pagamentos/asaas/webhook",
        "raw_path": b"/api/v1/pagamentos/asaas/webhook",
        "query_string": b"",
        "headers": [(b"content-type", b"application/json")],
        "client": ("testclient", 50001),
        "server": ("testserver", 80),
    }
    return Request(scope, receive)


def _call_webhook(payload: dict, db: SessionLocal) -> dict:
    req = _build_request(payload)
    return asyncio.run(asaas_webhook(req, db))


def _setup():
    init_db()
    db = SessionLocal()
    db.query(SaasSignupRequest).delete()
    db.query(ChatwootAccount).delete()
    db.query(AnamneseWorkflow).delete()
    db.query(AgendaEvento).delete()
    db.query(Contabilidade).delete()
    db.query(Pagamento).delete()
    db.query(Cliente).delete()
    db.query(Nutricionista).delete()
    db.query(Tenant).delete()
    db.commit()

    tenant = Tenant(nome="Tenant Payments", status="active", plano="pro")
    db.add(tenant)
    db.commit()
    db.refresh(tenant)

    nutri = Nutricionista(
        nome="Nutri Payments",
        email="nutri.payments@test.com",
        password_hash="hash",
        status="active",
        plano="pro",
        tenant_id=tenant.id,
        tipo_user="nutri",
    )
    db.add(nutri)
    db.commit()
    db.refresh(nutri)

    cliente = Cliente(
        nome="Cliente Pagamento",
        contato_chatwoot="cw-payment-1",
        status="cliente_potencial",
        nutricionista_id=nutri.id,
    )
    db.add(cliente)
    db.commit()
    db.refresh(cliente)

    pg = Pagamento(
        cliente_id=cliente.id,
        nutricionista_id=nutri.id,
        valor=390.0,
        metodo="pix",
        status="pendente",
        referencia="pay_test_webhook",
    )
    db.add(pg)
    db.commit()
    db.refresh(pg)

    contab = Contabilidade(
        tipo="pagamento_assas",
        valor=390,
        descricao="Cobrança teste",
        tenant_id=tenant.id,
        cliente_id=cliente.id,
        assas_id="pay_test_webhook",
        status="pendente",
    )
    db.add(contab)
    db.commit()
    return db, pg.id


def test_asaas_webhook_atualiza_pagamento_para_pago():
    db, pg_id = _setup()
    payload = {
        "event": "PAYMENT_RECEIVED",
        "payment": {"id": "pay_test_webhook", "status": "RECEIVED"},
    }
    response = _call_webhook(payload, db)
    assert response["status"] == "ok"
    pg = db.query(Pagamento).filter(Pagamento.id == pg_id).first()
    assert pg is not None
    assert pg.status == "pago"
    contab = db.query(Contabilidade).filter(Contabilidade.assas_id == "pay_test_webhook").first()
    assert contab is not None
    assert contab.status == "pago"
    db.close()


def test_asaas_webhook_inicia_fluxo_anamnese_quando_consulta_futura_existe():
    db, pg_id = _setup()
    pagamento = db.query(Pagamento).filter(Pagamento.id == pg_id).first()
    assert pagamento is not None
    nutri = db.query(Nutricionista).filter(Nutricionista.id == pagamento.nutricionista_id).first()
    assert nutri is not None

    evento = AgendaEvento(
        tenant_id=nutri.tenant_id,
        nutricionista_id=pagamento.nutricionista_id,
        cliente_id=pagamento.cliente_id,
        titulo="Consulta inicial",
        descricao="Consulta agendada",
        inicio_em=datetime.now(UTC).replace(tzinfo=None) + timedelta(days=4),
        fim_em=datetime.now(UTC).replace(tzinfo=None) + timedelta(days=4, minutes=50),
        status="agendado",
        origem="painel",
        criado_em=datetime.utcnow(),
        atualizado_em=datetime.utcnow(),
    )
    db.add(evento)
    db.commit()

    payload = {
        "event": "PAYMENT_RECEIVED",
        "payment": {"id": "pay_test_webhook", "status": "RECEIVED"},
    }
    response = _call_webhook(payload, db)
    assert response["status"] == "ok"

    wf = (
        db.query(AnamneseWorkflow)
        .filter(AnamneseWorkflow.cliente_id == pagamento.cliente_id)
        .order_by(AnamneseWorkflow.id.desc())
        .first()
    )
    assert wf is not None
    assert wf.status in {"pending", "in_progress"}
    assert wf.prazo_conclusao_em is not None
    assert wf.pagamento_id == pagamento.id
    db.close()


def test_asaas_webhook_provisiona_assinatura_saas_quando_pago():
    db, _ = _setup()
    signup = SaasSignupRequest(
        nome="Nutri Nova",
        email="nutri.nova@teste.com",
        telefone="+5585999990000",
        plano_nome="pro",
        documento="00000000000",
        asaas_payment_id="pay_saas_001",
        asaas_customer_id="cus_saas_001",
        payment_status="pendente",
    )
    db.add(signup)
    db.commit()

    payload = {
        "event": "PAYMENT_RECEIVED",
        "payment": {"id": "pay_saas_001", "status": "RECEIVED"},
    }
    response = _call_webhook(payload, db)
    assert response["status"] == "ok"
    assert response["scope"] == "saas_signup"

    db.refresh(signup)
    assert signup.payment_status == "pago"
    assert signup.provisioned_nutricionista_id is not None
    assert signup.provisioned_chatwoot_account is not None

    criada = db.query(Nutricionista).filter(Nutricionista.email == "nutri.nova@teste.com").first()
    assert criada is not None
    conta = db.query(ChatwootAccount).filter(ChatwootAccount.nutricionista_id == criada.id).first()
    assert conta is not None
    db.close()
