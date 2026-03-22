from sqlalchemy import Column, DateTime, Integer, String

from app.domain.models.base import Base


class SaasSignupRequest(Base):
    __tablename__ = "saas_signup_requests"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    email = Column(String, nullable=False, index=True)
    telefone = Column(String, nullable=True)
    plano_nome = Column(String, nullable=False)
    documento = Column(String, nullable=True)
    asaas_payment_id = Column(String, nullable=False, unique=True, index=True)
    asaas_customer_id = Column(String, nullable=True)
    payment_status = Column(String, nullable=False, default="pendente")
    valor = Column(String, nullable=True)
    provisioned_tenant_id = Column(Integer, nullable=True)
    provisioned_nutricionista_id = Column(Integer, nullable=True)
    provisioned_chatwoot_account = Column(String, nullable=True)
    provisioned_em = Column(DateTime, nullable=True)
    criado_em = Column(DateTime, nullable=True)
    atualizado_em = Column(DateTime, nullable=True)
