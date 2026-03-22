import os
from datetime import UTC, datetime, timedelta
import json

os.environ["TEST_ENV"] = "1"

from app.api.v1.auth import get_password_hash
from app.db import SessionLocal, init_db
from app.domain.models.avanco import Avanco
from app.domain.models.cliente import Cliente
from app.domain.models.conversa import Conversa
from app.domain.models.nutricionista import Nutricionista
from app.domain.models.plano_alimentar import PlanoAlimentar
from app.domain.models.tenant import Tenant
from app.workers.meal_support_worker import process_notification_event


def _setup():
    init_db()
    db = SessionLocal()
    db.query(Avanco).delete()
    db.query(PlanoAlimentar).delete()
    db.query(Conversa).delete()
    db.query(Cliente).delete()
    db.query(Nutricionista).delete()
    db.query(Tenant).delete()
    db.commit()

    tenant = Tenant(nome="Tenant Meal", status="active", plano="pro")
    db.add(tenant)
    db.commit()
    db.refresh(tenant)

    nutri = Nutricionista(
        nome="Nutri Meal",
        email="nutri.meal@test.com",
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
        nome="Cliente Meal",
        contato_chatwoot="+5511999990000",
        status="cliente_ativo",
        nutricionista_id=nutri.id,
    )
    db.add(cliente)
    db.commit()
    db.refresh(cliente)

    conv = Conversa(
        cliente_id=cliente.id,
        nutricionista_id=nutri.id,
        mensagem="canal ativo",
        data=datetime.utcnow(),
        modo="ia",
        chatwoot_account_id="acct-1",
        chatwoot_conversation_id="conv-1",
    )
    db.add(conv)
    db.commit()

    now = datetime.now(UTC).replace(tzinfo=None, second=0, microsecond=0)
    refeicoes = [
        {"nome": "almoco", "horario": (now + timedelta(minutes=60)).strftime("%H:%M")},
        {"nome": "jantar", "horario": (now - timedelta(minutes=60)).strftime("%H:%M")},
    ]
    plano = PlanoAlimentar(
        cliente_id=cliente.id,
        nutricionista_id=nutri.id,
        titulo="Plano Meal",
        refeicoes=json.dumps(refeicoes, ensure_ascii=False),
        status="ativo",
    )
    db.add(plano)
    db.commit()
    return db, tenant, nutri, cliente


def test_meal_followup_tick_envia_pre_e_pos_e_registra_avanco(monkeypatch):
    db, tenant, nutri, cliente = _setup()
    sent = []
    monkeypatch.setattr(
        "app.workers.meal_support_worker.enviar_mensagens",
        lambda _a, _c, msgs: sent.extend(msgs),
    )

    process_notification_event(
        {
            "event_id": "evt-meal-1",
            "payload": {
                "tipo": "meal_followup_tick",
                "tenant_id": tenant.id,
                "nutricionista_id": nutri.id,
                "cliente_id": cliente.id,
            },
        }
    )

    assert len(sent) >= 2
    assert any("60 min para sua refeição" in m for m in sent)
    assert any("confirmar sua refeição" in m for m in sent)
    avancos = db.query(Avanco).filter(Avanco.cliente_id == cliente.id).all()
    assert len(avancos) >= 2
    db.close()
