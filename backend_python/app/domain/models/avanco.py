from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.domain.models.base import Base

class Avanco(Base):
    __tablename__ = "avancos"
    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    nutricionista_id = Column(Integer, ForeignKey("nutricionistas.id"), nullable=False)
    data = Column(DateTime)
    descricao = Column(Text)
    status = Column(String, default="aberto")  # aberto, em_progresso, concluido

    cliente = relationship("Cliente")
    nutricionista = relationship("Nutricionista")
