from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_register_and_token():
    # garante que registro e login funcionam
    import time
    email = f"teste{int(time.time() * 1000)}@nutria.com"

    resp = client.post("/api/v1/auth/register", json={"username": "Teste", "email": email, "password": "senha123"})
    assert resp.status_code == 200
    assert "id" in resp.json()

    login_resp = client.post("/api/v1/auth/token", data={"username": email, "password": "senha123"})
    assert login_resp.status_code == 200
    data = login_resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    verify_resp = client.get("/api/v1/auth/verify", headers={"Authorization": f"Bearer {data['access_token']}"})
    assert verify_resp.status_code == 200
    assert verify_resp.json()["status"] == "valid"


def test_json_login_me_and_refresh():
    import time

    email = f"teste-json-{int(time.time() * 1000)}@nutria.com"

    register_resp = client.post(
        "/api/v1/auth/register",
        json={"username": "Teste JSON", "email": email, "password": "senha123"},
    )
    assert register_resp.status_code == 200

    login_resp = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "senha123"},
    )
    assert login_resp.status_code == 200
    login_data = login_resp.json()
    assert "access_token" in login_data
    assert "refresh_token" in login_data
    assert login_data["user"]["email"] == email

    me_resp = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {login_data['access_token']}"},
    )
    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == email

    refresh_resp = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": login_data["refresh_token"]},
    )
    assert refresh_resp.status_code == 200
    assert "access_token" in refresh_resp.json()
