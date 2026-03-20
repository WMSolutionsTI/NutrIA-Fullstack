from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.domain.models.base import Base

class PlanoAlimentar(Base):
    __tablename__ = "planos_alimentares"
    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    nutricionista_id = Column(Integer, ForeignKey("nutricionistas.id"), nullable=False)
    titulo = Column(String, nullable=False)
    descricao = Column(Text)
    macros = Column(Text)  # JSON string
    refeicoes = Column(Text)  # JSON string
    data_criado = Column(DateTime)
    data_atualizacao = Column(DateTime)
    status = Column(String, default="ativo")  # ativo, inativo, arquivado

    cliente = relationship("Cliente")
    nutricionista = relationship("Nutricionista")
