from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.domain.models.base import Base


class VoiceCall(Base):
    __tablename__ = "voice_calls"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    nutricionista_id = Column(Integer, ForeignKey("nutricionistas.id"), nullable=False, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=True, index=True)
    twilio_call_sid = Column(String, nullable=True, index=True)
    retell_call_id = Column(String, nullable=True, index=True)
    telefone_destino = Column(String, nullable=False)
    telefone_origem = Column(String, nullable=True)
    status = Column(String, nullable=False, default="queued")
    duracao_segundos = Column(Integer, nullable=True)
    transcricao = Column(Text, nullable=True)
    resumo = Column(Text, nullable=True)
    recording_url = Column(String, nullable=True)
    erro = Column(Text, nullable=True)
    criado_em = Column(DateTime, nullable=True)
    atualizado_em = Column(DateTime, nullable=True)

    tenant = relationship("Tenant")
    nutricionista = relationship("Nutricionista")
    cliente = relationship("Cliente")
