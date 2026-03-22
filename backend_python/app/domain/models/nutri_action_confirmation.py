from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.domain.models.base import Base


class NutriActionConfirmation(Base):
    __tablename__ = "nutri_action_confirmations"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    nutricionista_id = Column(Integer, ForeignKey("nutricionistas.id"), nullable=False, index=True)
    account_id = Column(String, nullable=True, index=True)
    conversation_id = Column(String, nullable=True, index=True)
    token = Column(String, nullable=False, index=True)
    status = Column(String, nullable=False, default="pending")  # pending, confirmed, cancelled, expired
    action_payload = Column(Text, nullable=False)
    expires_em = Column(DateTime, nullable=True)
    criado_em = Column(DateTime, nullable=True)
    atualizado_em = Column(DateTime, nullable=True)

    tenant = relationship("Tenant")
    nutricionista = relationship("Nutricionista")

