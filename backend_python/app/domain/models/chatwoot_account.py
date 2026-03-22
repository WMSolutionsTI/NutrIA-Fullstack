from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.domain.models.base import Base


class ChatwootAccount(Base):
    __tablename__ = "chatwoot_accounts"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, unique=True)
    nutricionista_id = Column(Integer, ForeignKey("nutricionistas.id"), nullable=False, unique=True)
    chatwoot_account_id = Column(String, nullable=False, unique=True)
    chatwoot_account_external_id = Column(String, nullable=True, unique=True, index=True)
    chatwoot_instance = Column(String, nullable=False, default="cw-01")
    status = Column(String, nullable=False, default="active")
    limite_inboxes_base = Column(Integer, nullable=False, default=1)
    inboxes_extra = Column(Integer, nullable=False, default=0)
    criado_em = Column(DateTime)
    atualizado_em = Column(DateTime)
    observacoes = Column(String)

    tenant = relationship("Tenant")
    nutricionista = relationship("Nutricionista")
