from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.models.base import Base

class Campanha(Base):
    __tablename__ = "campanhas"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    descricao = Column(String)
    tipo = Column(String, nullable=False)  # Ex: "marketing", "automacao_ia"
    status = Column(String, default="ativa")
    criado_em = Column(DateTime)
    atualizado_em = Column(DateTime)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=True)
    tenant = relationship("Tenant")
    caixa_id = Column(Integer, ForeignKey("caixas_de_entrada.id"), nullable=True)
    caixa = relationship("CaixaDeEntrada")