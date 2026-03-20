from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_register_and_token():
    # garante que registro e login funcionam
    resp = client.post("/api/v1/auth/register", json={"username": "Teste", "email": "teste@nutria.com", "password": "senha123"})
    assert resp.status_code == 200
    assert "id" in resp.json()

    login_resp = client.post("/api/v1/auth/token", data={"username": "teste@nutria.com", "password": "senha123"})
    assert login_resp.status_code == 200
    data = login_resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

    verify_resp = client.get("/api/v1/auth/verify", headers={"Authorization": f"Bearer {data['access_token']}"})
    assert verify_resp.status_code == 200
    assert verify_resp.json()["status"] == "valid"
