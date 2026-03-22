from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.domain.models.base import Base


class AgendaEvento(Base):
    __tablename__ = "agenda_eventos"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    nutricionista_id = Column(Integer, ForeignKey("nutricionistas.id"), nullable=False, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=True, index=True)
    titulo = Column(String, nullable=False)
    descricao = Column(Text, nullable=True)
    inicio_em = Column(DateTime, nullable=False)
    fim_em = Column(DateTime, nullable=False)
    status = Column(String, nullable=False, default="agendado")
    modalidade = Column(String, nullable=True)  # online | presencial
    google_event_id = Column(String, nullable=True)
    origem = Column(String, nullable=False, default="painel")
    criado_em = Column(DateTime, nullable=True)
    atualizado_em = Column(DateTime, nullable=True)

    tenant = relationship("Tenant")
    nutricionista = relationship("Nutricionista")
    cliente = relationship("Cliente")
