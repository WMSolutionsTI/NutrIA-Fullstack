from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.domain.models.base import Base

class Prompt(Base):
    __tablename__ = "prompts"
    id = Column(Integer, primary_key=True, index=True)
    funcao = Column(String, nullable=False)  # Ex: "nutricionista", "admin", "contabilidade", "marketing"
    contexto = Column(String, nullable=False)  # Contexto base para IA
    texto = Column(String, nullable=False)  # Prompt principal
    criado_em = Column(DateTime)
    atualizado_em = Column(DateTime)
    ativo = Column(Integer, default=1)
    # Relacionamento opcional com tenant, caixa, etc.
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=True)
    tenant = relationship("Tenant")
    caixa_id = Column(Integer, ForeignKey("caixas_de_entrada.id"), nullable=True)
    caixa = relationship("CaixaDeEntrada")