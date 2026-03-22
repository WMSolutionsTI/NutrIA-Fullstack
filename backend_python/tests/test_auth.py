import os
import time

os.environ["TEST_ENV"] = "1"

from app.api.v1.auth import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    get_current_user,
    login,
    me,
    refresh,
    register,
    verify_token,
)
from app.db import SessionLocal, init_db
from app.domain.models.nutricionista import Nutricionista


def _fresh_db() -> SessionLocal:
    init_db()
    db = SessionLocal()
    db.query(Nutricionista).delete()
    db.commit()
    return db


def test_register_and_verify_token():
    db = _fresh_db()
    email = f"teste{int(time.time() * 1000)}@nutria.com"

    reg = register(
        RegisterRequest(username="Teste", email=email, password="senha123"),
        db,
    )
    assert "id" in reg

    login_data = login(LoginRequest(email=email, password="senha123"), db)
    assert "access_token" in login_data
    assert login_data["token_type"] == "bearer"

    verify_resp = verify_token(login_data["access_token"])
    assert verify_resp["status"] == "valid"
    assert verify_resp["email"] == email
    db.close()


def test_json_login_me_and_refresh():
    db = _fresh_db()
    email = f"teste-json-{int(time.time() * 1000)}@nutria.com"

    register(RegisterRequest(username="Teste JSON", email=email, password="senha123"), db)
    login_resp = login(LoginRequest(email=email, password="senha123"), db)

    assert "access_token" in login_resp
    assert "refresh_token" in login_resp
    assert login_resp["user"]["email"] == email

    current_user = get_current_user(login_resp["access_token"], db)
    me_resp = me(current_user)
    assert me_resp["email"] == email

    refresh_resp = refresh(RefreshRequest(refresh_token=login_resp["refresh_token"]))
    assert "access_token" in refresh_resp
    db.close()
