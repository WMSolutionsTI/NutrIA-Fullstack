from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.domain.models.base import Base

class CaixaDeEntrada(Base):
    __tablename__ = "caixas_de_entrada"
    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(String, nullable=False)  # whatsapp, instagram, etc
    identificador_chatwoot = Column(String, nullable=False)
    status = Column(String, default="active")
    data_aquisicao = Column(String)
    nutricionista_id = Column(Integer, ForeignKey("nutricionistas.id"))
    nutricionista = relationship("Nutricionista", back_populates="caixas_de_entrada")