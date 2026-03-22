import os
import uuid
from datetime import datetime

import pytest
from fastapi import HTTPException

os.environ["TEST_ENV"] = "1"

from app.api.v1.arquivo import executar_ocr_arquivo
from app.db import SessionLocal, init_db
from app.domain.models.arquivo import Arquivo
from app.domain.models.avanco import Avanco
from app.domain.models.cliente import Cliente
from app.domain.models.nutricionista import Nutricionista
from app.domain.models.tenant import Tenant
from app.services.ocr_service import extract_text_from_file


def _reset_db(db):
    db.query(Avanco).delete()
    db.query(Arquivo).delete()
    db.query(Cliente).delete()
    db.query(Nutricionista).delete()
    db.query(Tenant).delete()
    db.commit()


def _create_nutri(db, *, tenant_name: str, email: str) -> Nutricionista:
    tenant = Tenant(nome=tenant_name, status="active", plano="pro")
    db.add(tenant)
    db.commit()
    db.refresh(tenant)

    nutri = Nutricionista(
        nome=f"Nutri {tenant_name}",
        email=email,
        password_hash="hash",
        plano="pro",
        status="active",
        tenant_id=tenant.id,
        tipo_user="nutri",
    )
    db.add(nutri)
    db.commit()
    db.refresh(nutri)
    return nutri


def test_extract_text_from_file_plain_text_ok(tmp_path):
    content = "Plano alimentar da cliente Aline"
    path = tmp_path / "plano.txt"
    path.write_text(content, encoding="utf-8")

    result = extract_text_from_file(str(path), filename="plano.txt")

    assert result.status == "ok"
    assert result.engine == "plain_text"
    assert "Aline" in result.text


def test_executar_ocr_arquivo_persiste_resultado_e_avanco(monkeypatch):
    init_db()
    db = SessionLocal()
    try:
        _reset_db(db)
        nutri = _create_nutri(db, tenant_name="T1", email=f"{uuid.uuid4()}@test.com")
        cliente = Cliente(
            nome="Cliente OCR",
            contato_chatwoot=f"chat-{uuid.uuid4()}",
            status="cliente_ativo",
            nutricionista_id=nutri.id,
            historico="{}",
        )
        db.add(cliente)
        db.commit()
        db.refresh(cliente)

        arquivo = Arquivo(
            nome="documento.txt",
            tipo="documento",
            caminho_s3="tenant/documents/documento.txt",
            tamanho=21,
            tenant_id=nutri.tenant_id,
            cliente_id=cliente.id,
            conversa_id=None,
            criado_em=datetime.utcnow(),
        )
        db.add(arquivo)
        db.commit()
        db.refresh(arquivo)

        def fake_download_object(object_name: str, file_path: str):
            assert object_name == "tenant/documents/documento.txt"
            with open(file_path, "w", encoding="utf-8") as fh:
                fh.write("Texto OCR para prontuário.")
            return True

        monkeypatch.setattr("app.api.v1.arquivo.download_object", fake_download_object)

        payload = executar_ocr_arquivo(arquivo.id, True, db, nutri)
        assert payload["ocr_status"] == "ok"
        assert payload["ocr_engine"] == "plain_text"

        db.refresh(arquivo)
        assert arquivo.ocr_status == "ok"
        assert arquivo.ocr_texto is not None
        assert "prontuário" in arquivo.ocr_texto

        avanco = db.query(Avanco).filter(Avanco.cliente_id == cliente.id).order_by(Avanco.id.desc()).first()
        assert avanco is not None
        assert "[OCR_ARQUIVO]" in (avanco.descricao or "")
    finally:
        db.close()


def test_executar_ocr_arquivo_bloqueia_tenant_diferente(monkeypatch):
    init_db()
    db = SessionLocal()
    try:
        _reset_db(db)
        nutri_a = _create_nutri(db, tenant_name="T1", email=f"a-{uuid.uuid4()}@test.com")
        nutri_b = _create_nutri(db, tenant_name="T2", email=f"b-{uuid.uuid4()}@test.com")

        arquivo = Arquivo(
            nome="isolamento.txt",
            tipo="documento",
            caminho_s3="tenant-1/docs/isolamento.txt",
            tamanho=10,
            tenant_id=nutri_a.tenant_id,
            cliente_id=None,
            conversa_id=None,
            criado_em=datetime.utcnow(),
        )
        db.add(arquivo)
        db.commit()
        db.refresh(arquivo)

        monkeypatch.setattr("app.api.v1.arquivo.download_object", lambda *_args, **_kwargs: True)

        with pytest.raises(HTTPException) as exc:
            executar_ocr_arquivo(arquivo.id, False, db, nutri_b)
        assert exc.value.status_code == 403
    finally:
        db.close()
