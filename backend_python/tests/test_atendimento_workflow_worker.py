import os
from datetime import UTC, datetime, timedelta

os.environ["TEST_ENV"] = "1"

from app.api.v1.auth import get_password_hash
from app.db import SessionLocal, init_db
from app.domain.models.agenda_evento import AgendaEvento
from app.domain.models.avanco import Avanco
from app.domain.models.cliente import Cliente
from app.domain.models.contabilidade import Contabilidade
from app.domain.models.conversa import Conversa
from app.domain.models.nutricionista import Nutricionista
from app.domain.models.pagamento import Pagamento
from app.domain.models.tenant import Tenant
from app.workers.atendimento_workflow_worker import process_atendimento_workflow


def _setup():
    init_db()
    db = SessionLocal()
    db.query(AgendaEvento).delete()
    db.query(Avanco).delete()
    db.query(Contabilidade).delete()
    db.query(Pagamento).delete()
    db.query(Conversa).delete()
    db.query(Cliente).delete()
    db.query(Nutricionista).delete()
    db.query(Tenant).delete()
    db.commit()

    tenant = Tenant(nome="Tenant Workflow", status="active", plano="pro")
    db.add(tenant)
    db.commit()
    db.refresh(tenant)

    nutri = Nutricionista(
        nome="Nutri Workflow",
        email="nutri.workflow@test.com",
        password_hash=get_password_hash("senha123"),
        status="active",
        plano="pro",
        tenant_id=tenant.id,
        tipo_user="nutri",
        auditoria="Contexto da nutri teste.",
    )
    db.add(nutri)
    db.commit()
    db.refresh(nutri)

    cliente = Cliente(
        nome="Cliente Workflow",
        contato_chatwoot="cw-workflow-1",
        status="cliente_ativo",
        nutricionista_id=nutri.id,
    )
    db.add(cliente)
    db.commit()
    db.refresh(cliente)
    return db, tenant, nutri, cliente


def test_worker_processa_evento_chatwoot_e_salva_resposta():
    db, tenant, nutri, cliente = _setup()
    payload = {
        "event_id": "evt-workflow-1",
        "tenant_id": tenant.id,
        "nutricionista_id": nutri.id,
        "cliente_id": cliente.id,
        "payload": {
            "account_id": "acct123",
            "inbox_id": "inbox-123",
            "canal": "whatsapp",
            "conversation_id": "conv-1",
            "message": "Oi, quero marcar consulta",
            "retry_count": 0,
        },
    }
    result = process_atendimento_workflow(payload)
    assert result["status"] == "ok"

    conversa = (
        db.query(Conversa)
        .filter(Conversa.cliente_id == cliente.id, Conversa.chatwoot_conversation_id == "conv-1")
        .order_by(Conversa.id.desc())
        .first()
    )
    assert conversa is not None
    assert conversa.chatwoot_account_id == "acct123"
    assert conversa.canal_origem == "whatsapp"
    db.close()


def test_worker_falha_reenfileira(monkeypatch):
    db, tenant, nutri, cliente = _setup()
    monkeypatch.setattr(
        "app.workers.atendimento_workflow_worker.gerar_resposta_agente",
        lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("falha_ia")),
    )
    payload = {
        "event_id": "evt-workflow-2",
        "tenant_id": tenant.id,
        "nutricionista_id": nutri.id,
        "cliente_id": cliente.id,
        "payload": {
            "account_id": "acct123",
            "inbox_id": "inbox-123",
            "canal": "whatsapp",
            "conversation_id": "conv-2",
            "message": "Teste",
            "retry_count": 0,
        },
    }
    result = process_atendimento_workflow(payload)
    assert result["status"] in {"retry_enqueued", "failed"}
    db.close()


def test_worker_fluxo_comercial_responde_formas_pagamento(monkeypatch):
    db, tenant, nutri, cliente = _setup()
    db.add(
        AgendaEvento(
            tenant_id=tenant.id,
            nutricionista_id=nutri.id,
            cliente_id=cliente.id,
            titulo="Consulta inicial",
            descricao="teste",
            inicio_em=datetime.now(UTC).replace(tzinfo=None) + timedelta(days=2),
            fim_em=datetime.now(UTC).replace(tzinfo=None) + timedelta(days=2, minutes=50),
            status="agendado",
            origem="painel",
            criado_em=datetime.utcnow(),
            atualizado_em=datetime.utcnow(),
        )
    )
    db.commit()
    sent = []
    monkeypatch.setattr(
        "app.workers.atendimento_workflow_worker.enviar_mensagens",
        lambda _a, _c, msgs: sent.extend(msgs),
    )
    monkeypatch.setattr(
        "app.workers.atendimento_workflow_worker._planner_comercial",
        lambda **_kwargs: {
            "action": "answer_payment_options",
            "package_months": 3,
            "billing_type": "UNKNOWN",
            "value_brl": 0,
            "customer_email": "",
            "customer_cpf_cnpj": "",
            "confidence": 0.92,
            "reason": "cliente pediu formas de pagamento",
        },
    )

    payload = {
        "event_id": "evt-workflow-3",
        "tenant_id": tenant.id,
        "nutricionista_id": nutri.id,
        "cliente_id": cliente.id,
        "payload": {
            "account_id": "acct123",
            "inbox_id": "inbox-123",
            "canal": "whatsapp",
            "conversation_id": "conv-3",
            "message": "Quero contratar o pacote de 3 meses, quais as formas de pagamento?",
            "retry_count": 0,
        },
    }
    result = process_atendimento_workflow(payload)
    assert result["status"] == "ok"
    assert any("formas de pagamento" in m.lower() or "pix" in m.lower() for m in sent)
    db.close()


def test_worker_fluxo_comercial_gera_checkout_e_salva_pagamento(monkeypatch):
    db, tenant, nutri, cliente = _setup()
    db.add(
        AgendaEvento(
            tenant_id=tenant.id,
            nutricionista_id=nutri.id,
            cliente_id=cliente.id,
            titulo="Consulta inicial",
            descricao="teste",
            inicio_em=datetime.now(UTC).replace(tzinfo=None) + timedelta(days=2),
            fim_em=datetime.now(UTC).replace(tzinfo=None) + timedelta(days=2, minutes=50),
            status="agendado",
            origem="painel",
            criado_em=datetime.utcnow(),
            atualizado_em=datetime.utcnow(),
        )
    )
    db.commit()
    sent = []
    monkeypatch.setattr(
        "app.workers.atendimento_workflow_worker.enviar_mensagens",
        lambda _a, _c, msgs: sent.extend(msgs),
    )
    monkeypatch.setattr("app.workers.atendimento_workflow_worker.is_configured", lambda *_args, **_kwargs: True)
    monkeypatch.setattr(
        "app.workers.atendimento_workflow_worker.load_asaas_config_from_user",
        lambda *_args, **_kwargs: {"api_key": "asaas_key_test", "api_url": "https://api-sandbox.asaas.com/v3"},
    )
    monkeypatch.setattr(
        "app.workers.atendimento_workflow_worker._planner_comercial",
        lambda **_kwargs: {
            "action": "create_payment_link",
            "package_months": 3,
            "billing_type": "PIX",
            "value_brl": 390.0,
            "customer_email": "cliente@teste.com",
            "customer_cpf_cnpj": "",
            "confidence": 0.95,
            "reason": "cliente quer fechar no pix",
        },
    )
    monkeypatch.setattr(
        "app.workers.atendimento_workflow_worker.create_customer",
        lambda **_kwargs: {"id": "cus_test_1"},
    )
    monkeypatch.setattr(
        "app.workers.atendimento_workflow_worker.create_payment",
        lambda **_kwargs: {
            "id": "pay_test_1",
            "invoiceUrl": "https://pay.example/checkout/pay_test_1",
            "dueDate": "2026-03-30",
        },
    )

    payload = {
        "event_id": "evt-workflow-4",
        "tenant_id": tenant.id,
        "nutricionista_id": nutri.id,
        "cliente_id": cliente.id,
        "payload": {
            "account_id": "acct123",
            "inbox_id": "inbox-123",
            "canal": "whatsapp",
            "conversation_id": "conv-4",
            "message": "Fechar no pix agora",
            "retry_count": 0,
        },
    }
    result = process_atendimento_workflow(payload)
    assert result["status"] == "ok"

    pagamento = db.query(Pagamento).filter(Pagamento.referencia == "pay_test_1").first()
    assert pagamento is not None
    assert pagamento.status == "pendente"

    contab = db.query(Contabilidade).filter(Contabilidade.assas_id == "pay_test_1").first()
    assert contab is not None
    assert any("checkout" in m.lower() or "link" in m.lower() for m in sent)
    db.close()


def test_worker_registra_feedback_refeicao_no_prontuario():
    db, tenant, nutri, cliente = _setup()
    payload = {
        "event_id": "evt-workflow-meal-feedback",
        "tenant_id": tenant.id,
        "nutricionista_id": nutri.id,
        "cliente_id": cliente.id,
        "payload": {
            "account_id": "acct123",
            "inbox_id": "inbox-123",
            "canal": "whatsapp",
            "conversation_id": "conv-feedback",
            "message": "Tive dificuldade na refeição e fiz substituição no prato.",
            "retry_count": 0,
        },
    }
    process_atendimento_workflow(payload)
    avanco = (
        db.query(Avanco)
        .filter(Avanco.cliente_id == cliente.id, Avanco.descricao.like("%MEAL_FEEDBACK%"))
        .order_by(Avanco.id.desc())
        .first()
    )
    assert avanco is not None
    db.close()
