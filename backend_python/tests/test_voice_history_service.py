import os
import tempfile

os.environ["TEST_ENV"] = "1"

from app.api.v1.auth import get_password_hash
from app.db import SessionLocal, init_db
from app.domain.models.arquivo import Arquivo
from app.domain.models.cliente import Cliente
from app.domain.models.conversa import Conversa
from app.domain.models.nutricionista import Nutricionista
from app.domain.models.tenant import Tenant
from app.services.voice_history_service import persist_audio_from_local_file


def _setup():
    init_db()
    db = SessionLocal()
    db.query(Arquivo).delete()
    db.query(Conversa).delete()
    db.query(Cliente).delete()
    db.query(Nutricionista).delete()
    db.query(Tenant).delete()
    db.commit()

    tenant = Tenant(nome="Tenant Voice History", status="active", plano="pro")
    db.add(tenant)
    db.commit()
    db.refresh(tenant)

    nutri = Nutricionista(
        nome="Nutri VH",
        email="nutri.vh@test.com",
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
        nome="Cliente VH",
        contato_chatwoot="chatwoot-vh-1",
        status="cliente_ativo",
        nutricionista_id=nutri.id,
    )
    db.add(cliente)
    db.commit()
    db.refresh(cliente)
    return db, tenant, nutri, cliente


def test_persist_audio_local_file_cria_arquivo_e_log(monkeypatch):
    db, tenant, nutri, cliente = _setup()
    monkeypatch.setattr("app.services.voice_history_service.upload_object", lambda *_args, **_kwargs: True)

    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
        tmp.write(b"fake-audio-content")
        local_path = tmp.name

    try:
        result = persist_audio_from_local_file(
            db,
            tenant_id=tenant.id,
            nutricionista_id=nutri.id,
            cliente_id=cliente.id,
            local_path=local_path,
            original_filename="teste_audio.mp3",
            nota_conversa="[VOICE_RECORDING] teste",
        )
        assert result is not None
        arquivo = db.query(Arquivo).filter(Arquivo.id == result["arquivo_id"]).first()
        assert arquivo is not None
        assert arquivo.tipo == "audio"
        conversa = (
            db.query(Conversa)
            .filter(Conversa.cliente_id == cliente.id)
            .order_by(Conversa.id.desc())
            .first()
        )
        assert conversa is not None
        assert "[VOICE_RECORDING]" in conversa.mensagem
    finally:
        if os.path.exists(local_path):
            os.remove(local_path)
        db.close()

