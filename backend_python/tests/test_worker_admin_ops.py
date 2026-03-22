import os

os.environ["TEST_ENV"] = "1"

from app.db import SessionLocal, init_db
from app.domain.models.nutricionista import Nutricionista
from app.domain.models.tenant import Tenant
from app.domain.models.worker_job import WorkerJob
from app.workers.worker_admin_ops import process_admin_ops


def _setup():
    init_db()
    db = SessionLocal()
    db.query(WorkerJob).delete()
    db.query(Nutricionista).delete()
    db.query(Tenant).delete()
    db.commit()
    return db


def test_admin_ops_chatwoot_system_state(monkeypatch):
    db = _setup()
    sent = []
    monkeypatch.setattr("app.workers.worker_admin_ops.set_if_not_exists", lambda *_args, **_kwargs: True)
    monkeypatch.setattr("app.workers.worker_admin_ops.enviar_mensagens", lambda _a, _c, msgs: sent.extend(msgs))
    monkeypatch.setattr("app.workers.worker_admin_ops.get_cache", lambda _k: None)
    monkeypatch.setattr(
        "app.workers.worker_admin_ops._parse_admin_action",
        lambda _msg: {"action": "system_state", "confidence": 0.99, "worker_service": "", "replicas": 0},
    )
    monkeypatch.setattr("app.workers.worker_admin_ops.status_do_sistema", lambda: "SaaS Metrics:\ntotal=10")

    process_admin_ops(
        {
            "event_id": "evt-admin-1",
            "payload": {
                "source": "chatwoot_admin",
                "account_id": "1",
                "conversation_id": "100",
                "message": "estado do servidor",
            },
        }
    )
    assert any("SaaS Metrics" in m for m in sent)
    db.close()


def test_admin_ops_chatwoot_scale_worker_requer_confirmacao(monkeypatch):
    db = _setup()
    sent = []
    cache = {}
    monkeypatch.setattr("app.workers.worker_admin_ops.set_if_not_exists", lambda *_args, **_kwargs: True)
    monkeypatch.setattr("app.workers.worker_admin_ops.enviar_mensagens", lambda _a, _c, msgs: sent.extend(msgs))
    monkeypatch.setattr(
        "app.workers.worker_admin_ops._parse_admin_action",
        lambda _msg: {
            "action": "scale_worker",
            "confidence": 0.95,
            "worker_service": "worker_atendimento",
            "replicas": 3,
        },
    )
    monkeypatch.setattr("app.workers.worker_admin_ops.set_cache", lambda k, v, expire=0: cache.__setitem__(k, v))
    monkeypatch.setattr("app.workers.worker_admin_ops.get_cache", lambda k: cache.get(k))
    monkeypatch.setattr("app.workers.worker_admin_ops.delete_cache", lambda k: cache.pop(k, None))
    monkeypatch.setattr(
        "app.workers.worker_admin_ops._execute_scale_worker",
        lambda service, replicas: f"ok scale {service}={replicas}",
    )

    base_event = {
        "event_id": "evt-admin-2",
        "payload": {
            "source": "chatwoot_admin",
            "account_id": "1",
            "conversation_id": "101",
            "message": "subir mais um container de worker",
        },
    }
    process_admin_ops(base_event)
    assert any("Confirma a operação?" in m for m in sent)

    token = None
    for msg in sent:
        if "confirmo " in msg:
            token = msg.split("confirmo ", 1)[1].split("`", 1)[0].strip()
            break
    assert token is not None

    sent.clear()
    process_admin_ops(
        {
            "event_id": "evt-admin-3",
            "payload": {
                "source": "chatwoot_admin",
                "account_id": "1",
                "conversation_id": "101",
                "message": f"confirmo {token}",
            },
        }
    )
    assert any("ok scale" in m for m in sent)
    db.close()


def test_admin_ops_chatwoot_envia_email_para_nutri(monkeypatch):
    db = _setup()
    sent = []
    cache = {}
    monkeypatch.setattr("app.workers.worker_admin_ops.set_if_not_exists", lambda *_args, **_kwargs: True)
    monkeypatch.setattr("app.workers.worker_admin_ops.enviar_mensagens", lambda _a, _c, msgs: sent.extend(msgs))
    monkeypatch.setattr("app.workers.worker_admin_ops.get_cache", lambda k: cache.get(k))
    monkeypatch.setattr(
        "app.workers.worker_admin_ops._parse_admin_action",
        lambda _msg: {
            "action": "send_email_nutri",
            "confidence": 0.95,
            "target_query": "nutri.comando@test.com",
            "message_content": "Aviso de manutenção programada hoje às 22h.",
            "subject": "Comunicado",
        },
    )
    monkeypatch.setattr("app.workers.worker_admin_ops._smtp_send", lambda *_args, **_kwargs: True)

    from app.api.v1.auth import get_password_hash
    from app.domain.models.nutricionista import Nutricionista
    from app.domain.models.tenant import Tenant

    tenant = Tenant(nome="tenant-admin-email", status="active", plano="pro")
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    nutri = Nutricionista(
        nome="Nutri Alvo",
        email="nutri.comando@test.com",
        password_hash=get_password_hash("senha123"),
        status="active",
        plano="pro",
        tenant_id=tenant.id,
        tipo_user="nutri",
    )
    db.add(nutri)
    db.commit()

    process_admin_ops(
        {
            "event_id": "evt-admin-4",
            "payload": {
                "source": "chatwoot_admin",
                "account_id": "1",
                "conversation_id": "102",
                "message": "enviar email",
            },
        }
    )
    assert any("E-mail enviado" in m for m in sent)
    db.close()
