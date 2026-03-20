from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.domain.models.base import Base

class Exame(Base):
    __tablename__ = "exames"
    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    nutricionista_id = Column(Integer, ForeignKey("nutricionistas.id"), nullable=False)
    nome = Column(String, nullable=False)
    tipo = Column(String, nullable=False)
    descricao = Column(Text)
    resultado = Column(Text)
    data_solicitacao = Column(DateTime)
    data_realizacao = Column(DateTime)
    status = Column(String, default="pendente")  # pendente, realizado, recebido

    cliente = relationship("Cliente")
    nutricionista = relationship("Nutricionista")
