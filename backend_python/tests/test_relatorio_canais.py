import os

os.environ["TEST_ENV"] = "1"

from app.api.v1.auth import get_password_hash
from app.api.v1.relatorio import ranking_canais
from app.db import SessionLocal, init_db
from app.domain.models.cliente import Cliente
from app.domain.models.conversa import Conversa
from app.domain.models.nutricionista import Nutricionista
from app.domain.models.tenant import Tenant


def _setup():
    init_db()
    db = SessionLocal()
    db.query(Conversa).delete()
    db.query(Cliente).delete()
    db.query(Nutricionista).delete()
    db.query(Tenant).delete()
    db.commit()

    tenant = Tenant(nome="Tenant Ranking", status="active", plano="pro")
    db.add(tenant)
    db.commit()
    db.refresh(tenant)

    nutri = Nutricionista(
        nome="Nutri Ranking",
        email="nutri.ranking@test.com",
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
        nome="Cliente Ranking",
        contato_chatwoot="cw-ranking-1",
        status="cliente_ativo",
        nutricionista_id=nutri.id,
    )
    db.add(cliente)
    db.commit()
    db.refresh(cliente)

    db.add_all(
        [
            Conversa(
                cliente_id=cliente.id,
                nutricionista_id=nutri.id,
                caixa_id=None,
                mensagem="m1",
                canal_origem="whatsapp",
            ),
            Conversa(
                cliente_id=cliente.id,
                nutricionista_id=nutri.id,
                caixa_id=None,
                mensagem="m2",
                canal_origem="whatsapp",
            ),
            Conversa(
                cliente_id=cliente.id,
                nutricionista_id=nutri.id,
                caixa_id=None,
                mensagem="m3",
                canal_origem="telegram",
            ),
        ]
    )
    db.commit()
    return db, nutri


def test_ranking_canais_agrega_por_canal():
    db, nutri = _setup()
    rows = ranking_canais(None, None, None, db, nutri)
    assert len(rows) >= 2
    assert rows[0]["canal"] == "whatsapp"
    assert rows[0]["total"] == 2
    db.close()

