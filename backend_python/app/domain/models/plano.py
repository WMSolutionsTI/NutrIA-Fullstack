from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.domain.models.base import Base

class Plano(Base):
    __tablename__ = "planos"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    descricao = Column(String)
    valor = Column(Integer, nullable=False)
    limite_caixas = Column(Integer, nullable=False)
    criado_em = Column(DateTime)
    atualizado_em = Column(DateTime)
    ativo = Column(Integer, default=1)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=True)
    tenant = relationship("Tenant")