from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.domain.models.base import Base

class Objetivo(Base):
    __tablename__ = "objetivos"
    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    nutricionista_id = Column(Integer, ForeignKey("nutricionistas.id"), nullable=False)
    titulo = Column(String, nullable=False)
    descricao = Column(Text)
    data_inicio = Column(DateTime)
    data_prevista = Column(DateTime)
    data_conclusao = Column(DateTime)
    status = Column(String, default="aberto")  # aberto, em_progresso, concluido, cancelado

    cliente = relationship("Cliente")
    nutricionista = relationship("Nutricionista")
