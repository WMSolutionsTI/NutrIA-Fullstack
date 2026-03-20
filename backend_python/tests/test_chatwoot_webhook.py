from fastapi.testclient import TestClient
from app.db import SessionLocal, init_db
from app.domain.models.nutricionista import Nutricionista
from app.domain.models.caixa_de_entrada import CaixaDeEntrada
from app.domain.models.cliente import Cliente
from main import app
from app.workers.atendimento_workflow_worker import process_atendimento_workflow

client = TestClient(app)


def setup_test_data():
    init_db()
    db = SessionLocal()
    db.query(Cliente).delete()
    db.query(CaixaDeEntrada).delete()
    db.query(Nutricionista).delete()
    db.commit()

    nutri = Nutricionista(
        nome="Nutri Teste",
        email="nutri.teste@teste.com",
        password_hash="hash",
        plano="basic",
        status="active",
        tipo_user="nutri"
    )
    db.add(nutri)
    db.commit()
    db.refresh(nutri)
    nutri_id = nutri.id

    caixa = CaixaDeEntrada(
        tipo="whatsapp",
        identificador_chatwoot="inbox-123",
        nutricionista_id=nutri_id
    )
    db.add(caixa)
    db.commit()
    db.refresh(caixa)
    db.close()
    return nutri_id, caixa


def test_chatwoot_webhook_cria_cliente_potencial():
    nutri_id, caixa = setup_test_data()
    payload = {
        "inbox_id": caixa.identificador_chatwoot,
        "conversation_id": "conv123",
        "account_id": "acct123",
        "sender": {"id": "chatwoot-contact-123"},
        "content": "Olá, gostaria de informações sobre planos"
    }
    response = client.post("/api/v1/chatwoot/webhook", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "potencial_em_atendimento"

    db = SessionLocal()
    cliente = db.query(Cliente).filter(Cliente.contato_chatwoot == "chatwoot-contact-123").first()
    assert cliente is not None
    assert cliente.status == "cliente_potencial"
    assert cliente.nutricionista_id == nutri_id
    db.close()


def test_atendimento_workflow_worker_engagement():
    result = process_atendimento_workflow({
        "account_id": "acct123",
        "conversation_id": "conv123",
        "message": "teste",
        "workflow": "potencial"
    })
    assert result["status"] == "ok"
    assert "potencial" in result["workflow"]
