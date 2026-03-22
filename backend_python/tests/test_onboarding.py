import time

from fastapi.testclient import TestClient

from app.db import SessionLocal, init_db
from app.domain.models.chatwoot_account import ChatwootAccount
from app.domain.models.nutricionista import Nutricionista
from app.domain.models.tenant import Tenant
from main import app

client = TestClient(app)


def test_confirmar_assinatura_cria_tenant_nutri_e_conta_chatwoot():
    init_db()
    email = f"onboarding-{int(time.time() * 1000)}@nutria.com"
    payload = {
        "pagamento_id": f"pay-{int(time.time())}",
        "nome": "Ana Teste",
        "email": email,
        "plano_nome": "pro",
        "documento": "12345678900",
        "telefone": "85999990000",
    }

    resp = client.post("/api/v1/onboarding/assinatura/confirmar", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "assinatura_confirmada"
    assert data["limite_inboxes"] >= 1

    db = SessionLocal()
    nutri = db.query(Nutricionista).filter(Nutricionista.email == email).first()
    assert nutri is not None

    tenant = db.query(Tenant).filter(Tenant.id == nutri.tenant_id).first()
    assert tenant is not None

    conta = db.query(ChatwootAccount).filter(ChatwootAccount.nutricionista_id == nutri.id).first()
    assert conta is not None
    assert conta.status == "active"
    db.close()
