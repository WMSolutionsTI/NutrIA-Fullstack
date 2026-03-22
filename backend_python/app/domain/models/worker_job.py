from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.domain.models.base import Base


class WorkerJob(Base):
    __tablename__ = "worker_jobs"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String, nullable=False, unique=True, index=True)
    queue = Column(String, nullable=False, index=True)
    tipo = Column(String, nullable=False, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    nutricionista_id = Column(Integer, ForeignKey("nutricionistas.id"), nullable=False, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=True, index=True)
    status = Column(String, nullable=False, default="queued")
    tentativas = Column(Integer, nullable=False, default=0)
    erro = Column(Text, nullable=True)
    payload = Column(Text, nullable=True)
    criado_em = Column(DateTime, nullable=True)
    atualizado_em = Column(DateTime, nullable=True)

    tenant = relationship("Tenant")
    nutricionista = relationship("Nutricionista")
    cliente = relationship("Cliente")
