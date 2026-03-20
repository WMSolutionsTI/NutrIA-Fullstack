from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.domain.models.base import Base

class Contabilidade(Base):
    __tablename__ = "contabilidades"
    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(String, nullable=False)  # Ex: "receita", "despesa", "assinatura", "pagamento_assas"
    valor = Column(Integer, nullable=False)
    descricao = Column(String)
    data = Column(DateTime)
    status = Column(String, default="pendente")
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=True)
    tenant = relationship("Tenant")
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=True)
    cliente = relationship("Cliente")
    assas_id = Column(String, nullable=True)  # ID de pagamento Assas