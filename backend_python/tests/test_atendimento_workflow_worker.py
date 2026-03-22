import os

os.environ["TEST_ENV"] = "1"

from app.api.v1.auth import get_password_hash
from app.db import SessionLocal, init_db
from app.domain.models.cliente import Cliente
from app.domain.models.conversa import Conversa
from app.domain.models.nutricionista import Nutricionista
from app.domain.models.tenant import Tenant
from app.workers.atendimento_workflow_worker import process_atendimento_workflow


def _setup():
    init_db()
    db = SessionLocal()
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

