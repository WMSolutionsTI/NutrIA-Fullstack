import os
from datetime import datetime

from app.api.v1.auth import get_password_hash
from app.api.v1.integracoes_google import callback_integracao_google
from app.db import SessionLocal, init_db
from app.domain.models.google_calendar_integration import GoogleCalendarIntegration
from app.domain.models.nutricionista import Nutricionista
from app.domain.models.tenant import Tenant

os.environ["GOOGLE_CLIENT_ID"] = "client"
os.environ["GOOGLE_CLIENT_SECRET"] = "secret"


def _setup():
    init_db()
    db = SessionLocal()
    db.query(GoogleCalendarIntegration).delete()
    db.query(Nutricionista).delete()
    db.query(Tenant).delete()
    db.commit()

    tenant = Tenant(nome="Tenant Google", status="active", plano="pro")
    db.add(tenant)
    db.commit()
    db.refresh(tenant)

    nutri = Nutricionista(
        nome="Nutri Google",
        email="nutri.google@test.com",
        password_hash=get_password_hash("senha123"),
        status="active",
        plano="pro",
        tenant_id=tenant.id,
        tipo_user="nutri",
    )
    db.add(nutri)
    db.commit()
    db.refresh(nutri)
    return db, nutri


def test_callback_google_persiste_integracao(monkeypatch):
    db, nutri = _setup()

    monkeypatch.setattr(
        "app.api.v1.integracoes_google._parse_state_token",
        lambda _: {"nutricionista_id": nutri.id},
    )
    monkeypatch.setattr(
        "app.api.v1.integracoes_google.exchange_code_for_token",
        lambda _: {"access_token": "access", "refresh_token": "refresh", "expires_in": 3600},
    )
    monkeypatch.setattr(
        "app.api.v1.integracoes_google.fetch_google_profile",
        lambda _: {"email": "google-account@test.com"},
    )

    response = callback_integracao_google("code", "state", db)
    assert response["status"] == "google_conectado"
    integration = (
        db.query(GoogleCalendarIntegration)
        .filter(GoogleCalendarIntegration.nutricionista_id == nutri.id)
        .first()
    )
    assert integration is not None
    assert integration.google_email == "google-account@test.com"
    assert integration.status == "active"
    assert integration.atualizado_em is not None
    db.close()
