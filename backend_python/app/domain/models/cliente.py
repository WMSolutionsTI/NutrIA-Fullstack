from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.domain.models.base import Base

class Cliente(Base):
    __tablename__ = "clientes"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    contato_chatwoot = Column(String, unique=True, nullable=True)
    status = Column(String, default="cliente_potencial")
    nutricionista_id = Column(Integer, ForeignKey("nutricionistas.id"))
    nutricionista = relationship("Nutricionista")
    historico = Column(String)  # JSON string or dict