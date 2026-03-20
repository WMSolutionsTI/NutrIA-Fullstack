from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.domain.models.base import Base

class AdminRequest(Base):
    __tablename__ = "admin_requests"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    nutricionista_id = Column(Integer, ForeignKey("nutricionistas.id"), nullable=True)
    tipo = Column(String, nullable=False)  # ex: caixa_inbox, upgrade, pagamento
    status = Column(String, default="pendente")
    descricao = Column(Text)
    criado_em = Column(DateTime)
    atualizado_em = Column(DateTime)

    tenant = relationship("Tenant")
    nutricionista = relationship("Nutricionista")
