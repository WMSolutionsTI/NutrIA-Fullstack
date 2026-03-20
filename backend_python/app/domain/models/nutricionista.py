from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.domain.models.base import Base

class Nutricionista(Base):
    __tablename__ = "nutricionistas"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    status = Column(String, default="active")
    plano = Column(String, nullable=False)
    tenant_id = Column(Integer, ForeignKey("tenants.id"))
    tenant = relationship("Tenant", back_populates="nutricionistas")
    caixas_de_entrada = relationship("CaixaDeEntrada", back_populates="nutricionista")
    permissoes = Column(String)  # JSON string or dict
    auditoria = Column(String)
    tipo_user = Column(String, default="nutri")  # 'nutri' ou 'cliente'
    contexto_ia = Column(String)  # JSON string ou dict com planos, horários, especialidade, etc