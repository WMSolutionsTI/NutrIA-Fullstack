from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.domain.models.base import Base

class Tenant(Base):
    __tablename__ = "tenants"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    status = Column(String, default="active")
    plano = Column(String, nullable=False)
    limites = Column(String)  # JSON string or dict
    auditoria = Column(String)
    nutricionistas = relationship("Nutricionista", back_populates="tenant")