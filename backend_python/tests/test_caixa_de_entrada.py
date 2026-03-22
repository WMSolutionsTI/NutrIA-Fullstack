import os
from datetime import UTC, datetime

from fastapi.testclient import TestClient

from app.api.v1.auth import get_password_hash
from app.db import SessionLocal, init_db
from app.domain.models.admin_request import AdminRequest
from app.domain.models.caixa_de_entrada import CaixaDeEntrada
from app.domain.models.chatwoot_account import ChatwootAccount
from app.domain.models.nutricionista import Nutricionista
from app.domain.models.tenant import Tenant
from main import app

os.environ["TEST_ENV"] = "1"

client = TestClient(app)


def setup_caixas_data():
    init_db()
    db = SessionLocal()
    db.query(AdminRequest).delete()
    db.query(CaixaDeEntrada).delete()
    db.query(ChatwootAccount).delete()
    db.query(Nutricionista).delete()
    db.query(Tenant).delete()
    db.commit()

    tenant_a = Tenant(nome="Tenant A", status="active", plano="pro")
    tenant_b = Tenant(nome="Tenant B", status="active", plano="basic")
    db.add(tenant_a)
    db.add(tenant_b)
    db.commit()
    db.refresh(tenant_a)
    db.refresh(tenant_b)

    nutri_a = Nutricionista(
        nome="Nutri A",
        email="nutri.a@test.com",
        password_hash=get_password_hash("senha123"),
        status="active",
        plano="pro",
        tenant_id=tenant_a.id,
        tipo_user="nutri",
    )
    nutri_b = Nutricionista(
        nome="Nutri B",
        email="nutri.b@test.com",
        password_hash=get_password_hash("senha123"),
        status="active",
        plano="basic",
        tenant_id=tenant_b.id,
        tipo_user="nutri",
    )
    db.add(nutri_a)
    db.add(nutri_b)
    db.commit()
    db.refresh(nutri_a)
    db.refresh(nutri_b)

    conta_a = ChatwootAccount(
        tenant_id=tenant_a.id,
        nutricionista_id=nutri_a.id,
        chatwoot_account_id=f"cw-{tenant_a.id}",
        chatwoot_instance="cw-01",
        status="active",
        limite_inboxes_base=1,
        inboxes_extra=0,
    )
    conta_b = ChatwootAccount(
        tenant_id=tenant_b.id,
        nutricionista_id=nutri_b.id,
        chatwoot_account_id=f"cw-{tenant_b.id}",
        chatwoot_instance="cw-01",
        status="active",
        limite_inboxes_base=2,
        inboxes_extra=0,
    )
    db.add(conta_a)
    db.add(conta_b)
    db.commit()

    caixa_a = CaixaDeEntrada(
        tipo="whatsapp",
        identificador_chatwoot="inbox-a-1",
        status="active",
        nutricionista_id=nutri_a.id,
        data_aquisicao=datetime.now(UTC).isoformat(),
    )
    db.add(caixa_a)
    db.commit()

    pend_a = AdminRequest(
        tenant_id=tenant_a.id,
        nutricionista_id=nutri_a.id,
        tipo="nova_integracao_inbox",
        status="pendente",
        descricao='{"tipo":"whatsapp"}',
        criado_em=datetime.now(UTC),
        atualizado_em=datetime.now(UTC),
    )
    pend_b = AdminRequest(
        tenant_id=tenant_b.id,
        nutricionista_id=nutri_b.id,
        tipo="nova_integracao_inbox",
        status="pendente",
        descricao='{"tipo":"telegram"}',
        criado_em=datetime.now(UTC),
        atualizado_em=datetime.now(UTC),
    )
    db.add(pend_a)
    db.add(pend_b)
    db.commit()
    db.close()


def get_token(email: str, password: str = "senha123") -> str:
    response = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    return response.json()["access_token"]


def auth_headers(email: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {get_token(email)}"}


def test_resumo_caixas_retorna_limites_e_uso_real():
    setup_caixas_data()
    response = client.get("/api/v1/caixas/resumo", headers=auth_headers("nutri.a@test.com"))
    assert response.status_code == 200
    data = response.json()
    assert data["limite_inboxes_base"] == 1
    assert data["inboxes_extra"] == 0
    assert data["limite_total"] == 1
    assert data["em_uso"] == 1
    assert data["disponiveis"] == 0


def test_pendencias_retorna_apenas_da_nutri_autenticada():
    setup_caixas_data()
    response = client.get("/api/v1/caixas/pendencias", headers=auth_headers("nutri.a@test.com"))
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["nutricionista_id"] is not None

    db = SessionLocal()
    nutri_a = db.query(Nutricionista).filter(Nutricionista.email == "nutri.a@test.com").first()
    db.close()
    assert data[0]["nutricionista_id"] == nutri_a.id


def test_criacao_caixa_acima_do_limite_retorna_403():
    setup_caixas_data()
    payload = {"tipo": "telegram", "detalhes_integracao": {"bot": "xpto"}}
    response = client.post("/api/v1/caixas", json=payload, headers=auth_headers("nutri.a@test.com"))
    assert response.status_code == 403
    assert "Limite de inboxes" in response.json()["detail"]


def test_compra_inbox_avulsa_aumenta_limite_no_resumo():
    setup_caixas_data()
    buy = client.post(
        "/api/v1/caixas/extras/comprar",
        json={"quantidade": 2},
        headers=auth_headers("nutri.a@test.com"),
    )
    assert buy.status_code == 200
    assert buy.json()["novo_limite_total"] == 3

    resumo = client.get("/api/v1/caixas/resumo", headers=auth_headers("nutri.a@test.com"))
    assert resumo.status_code == 200
    data = resumo.json()
    assert data["limite_total"] == 3
    assert data["disponiveis"] == 2
