import pytest
from fastapi import HTTPException

from app.api.v1.auth import get_password_hash
from app.api.v1.conversa import (
    alternar_modo_conversa,
    get_conversa,
    get_conversas_cliente,
)
from app.db import SessionLocal, init_db
from app.domain.models.cliente import Cliente
from app.domain.models.conversa import Conversa
from app.domain.models.nutricionista import Nutricionista
from app.domain.models.tenant import Tenant


def _setup_data():
    init_db()
    db = SessionLocal()
    db.query(Conversa).delete()
    db.query(Cliente).delete()
    db.query(Nutricionista).delete()
    db.query(Tenant).delete()
    db.commit()

    tenant_a = Tenant(nome="Tenant Conversa A", status="active", plano="pro")
    tenant_b = Tenant(nome="Tenant Conversa B", status="active", plano="basic")
    db.add(tenant_a)
    db.add(tenant_b)
    db.commit()
    db.refresh(tenant_a)
    db.refresh(tenant_b)

    nutri_a = Nutricionista(
        nome="Nutri Conversa A",
        email="nutri.conversa.a@test.com",
        password_hash=get_password_hash("senha123"),
        status="active",
        plano="pro",
        tenant_id=tenant_a.id,
        tipo_user="nutri",
    )
    nutri_b = Nutricionista(
        nome="Nutri Conversa B",
        email="nutri.conversa.b@test.com",
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

    cliente_a = Cliente(
        nome="Cliente A",
        contato_chatwoot="cw-conv-a",
        status="cliente_ativo",
        nutricionista_id=nutri_a.id,
    )
    cliente_b = Cliente(
        nome="Cliente B",
        contato_chatwoot="cw-conv-b",
        status="cliente_ativo",
        nutricionista_id=nutri_b.id,
    )
    db.add(cliente_a)
    db.add(cliente_b)
    db.commit()
    db.refresh(cliente_a)
    db.refresh(cliente_b)

    conversa_a = Conversa(
        cliente_id=cliente_a.id,
        nutricionista_id=nutri_a.id,
        caixa_id=None,
        mensagem="Mensagem A",
        modo="ia",
        em_conversa_direta=False,
    )
    conversa_b = Conversa(
        cliente_id=cliente_b.id,
        nutricionista_id=nutri_b.id,
        caixa_id=None,
        mensagem="Mensagem B",
        modo="ia",
        em_conversa_direta=False,
    )
    db.add(conversa_a)
    db.add(conversa_b)
    db.commit()
    db.refresh(conversa_a)
    db.refresh(conversa_b)
    return db, nutri_a, nutri_b, cliente_a, cliente_b, conversa_a, conversa_b


def test_nutri_nao_acessa_conversa_de_outra_nutri():
    db, nutri_a, _, _, _, _, conversa_b = _setup_data()
    with pytest.raises(HTTPException) as exc:
        get_conversa(conversa_b.id, db, nutri_a)
    assert exc.value.status_code == 403
    db.close()


def test_nutri_lista_apenas_conversas_do_proprio_cliente():
    db, nutri_a, _, cliente_a, cliente_b, _, _ = _setup_data()
    conversas = get_conversas_cliente(cliente_a.id, db, nutri_a)
    assert len(conversas) >= 1

    with pytest.raises(HTTPException) as exc:
        get_conversas_cliente(cliente_b.id, db, nutri_a)
    assert exc.value.status_code == 403
    db.close()


def test_nutri_nao_altera_modo_de_conversa_de_outra_nutri():
    db, nutri_a, _, _, _, _, conversa_b = _setup_data()
    with pytest.raises(HTTPException) as exc:
        alternar_modo_conversa(conversa_b.id, "direto", db, nutri_a)
    assert exc.value.status_code == 403
    db.close()
