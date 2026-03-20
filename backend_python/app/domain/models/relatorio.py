from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.domain.models.base import Base

class Relatorio(Base):
    __tablename__ = "relatorios"
    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(String, nullable=False)  # Ex: "analytics", "exportacao", "mensal", "nutricionista", "admin"
    descricao = Column(String)
    data_inicio = Column(DateTime)
    data_fim = Column(DateTime)
    arquivo = Column(String)  # Path ou nome do arquivo exportado
    criado_em = Column(DateTime)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=True)
    tenant = relationship("Tenant")
    caixa_id = Column(Integer, ForeignKey("caixas_de_entrada.id"), nullable=True)
    caixa = relationship("CaixaDeEntrada")