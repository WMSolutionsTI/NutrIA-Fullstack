from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.domain.models.base import Base

class Pagamento(Base):
    __tablename__ = "pagamentos"
    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    nutricionista_id = Column(Integer, ForeignKey("nutricionistas.id"), nullable=False)
    valor = Column(Float, nullable=False)
    metodo = Column(String, nullable=False)  # cartao, boleto, pix
    status = Column(String, default="pendente")  # pendente, pago, cancelado
    data_vencimento = Column(DateTime)
    data_pagamento = Column(DateTime)
    referencia = Column(String)

    cliente = relationship("Cliente")
    nutricionista = relationship("Nutricionista")
