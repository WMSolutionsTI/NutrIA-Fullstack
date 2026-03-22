from datetime import datetime, timedelta

from app.api.v1.agenda import criar_evento
from app.api.v1.agenda import AgendaEventoCreateRequest
from app.api.v1.auth import get_password_hash
from app.db import SessionLocal, init_db
from app.domain.models.google_calendar_integration import GoogleCalendarIntegration
from app.domain.models.nutricionista import Nutricionista
from app.domain.models.tenant import Tenant


def _setup():
    init_db()
    db = SessionLocal()
    from app.domain.models.agenda_evento import AgendaEvento

    db.query(AgendaEvento).delete()
    db.query(GoogleCalendarIntegration).delete()
    db.query(Nutricionista).delete()
    db.query(Tenant).delete()
    db.commit()

    tenant = Tenant(nome="Tenant Agenda", status="active", plano="pro")
    db.add(tenant)
    db.commit()
    db.refresh(tenant)

    nutri = Nutricionista(
        nome="Nutri Agenda",
        email="nutri.agenda@test.com",
        password_hash=get_password_hash("senha123"),
        status="active",
        plano="pro",
        tenant_id=tenant.id,
        tipo_user="nutri",
    )
    db.add(nutri)
    db.commit()
    db.refresh(nutri)

    integration = GoogleCalendarIntegration(
        tenant_id=tenant.id,
        nutricionista_id=nutri.id,
        google_email="nutri@test.com",
        calendar_id="primary",
        access_token_encrypted="token",
        refresh_token_encrypted="refresh",
        status="active",
        criado_em=datetime.utcnow(),
        atualizado_em=datetime.utcnow(),
    )
    db.add(integration)
    db.commit()
    return db, nutri


def test_criar_evento_agenda_publica_sync(monkeypatch):
    db, nutri = _setup()

    monkeypatch.setattr("app.api.v1.agenda.get_valid_google_access_token", lambda *_: "token")
    monkeypatch.setattr("app.api.v1.agenda.create_google_event", lambda *_, **__: {"id": "google-evt-1"})
    monkeypatch.setattr("app.api.v1.agenda.publish_event", lambda *_: True)

    agora = datetime.utcnow() + timedelta(days=1)
    response = criar_evento(
        AgendaEventoCreateRequest(
            titulo="Consulta inicial",
            descricao="Detalhes",
            inicio_em=agora,
            fim_em=agora + timedelta(hours=1),
            cliente_id=None,
        ),
        db,
        nutri,
    )
    assert response["status"] == "agendado"
    assert response["google_event_id"] == "google-evt-1"
    db.close()
