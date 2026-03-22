import os
import uuid

os.environ["TEST_ENV"] = "1"

from app.api.v1.onboarding import AsaasConfigRequest, configurar_integracao_asaas, status_integracao_asaas
from app.db import SessionLocal, init_db
from app.domain.models.nutricionista import Nutricionista
from app.domain.models.tenant import Tenant
from app.services.asaas_service import load_asaas_config_from_user


def test_configurar_integracao_asaas_por_nutricionista():
    init_db()
    db = SessionLocal()
    try:
        db.query(Nutricionista).delete()
        db.query(Tenant).delete()
        db.commit()

        tenant = Tenant(nome="Tenant Asaas", status="active", plano="pro")
        db.add(tenant)
        db.commit()
        db.refresh(tenant)

        nutri = Nutricionista(
            nome="Nutri Config",
            email=f"nutri-{uuid.uuid4()}@test.com",
            password_hash="hash",
            status="active",
            plano="pro",
            tenant_id=tenant.id,
            tipo_user="nutri",
        )
        db.add(nutri)
        db.commit()
        db.refresh(nutri)

        result = configurar_integracao_asaas(
            AsaasConfigRequest(
                api_key="asaas_test_key_123456789",
                api_url="https://api-sandbox.asaas.com/v3",
                webhook_token="whk_test",
                wallet_id="wallet-1",
            ),
            nutri,
            db,
        )
        assert result["status"] == "asaas_configurada"
        cfg = load_asaas_config_from_user(nutri)
        assert cfg["api_key"] == "asaas_test_key_123456789"
        assert cfg["wallet_id"] == "wallet-1"

        status = status_integracao_asaas(nutri)
        assert status["configured"] is True
        assert status["webhook_token_configured"] is True
    finally:
        db.close()
