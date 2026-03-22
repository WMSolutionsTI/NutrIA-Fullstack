from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.domain.models.base import Base


class AnamneseWorkflow(Base):
    __tablename__ = "anamnese_workflows"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    nutricionista_id = Column(Integer, ForeignKey("nutricionistas.id"), nullable=False, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False, index=True)
    agenda_evento_id = Column(Integer, ForeignKey("agenda_eventos.id"), nullable=True, index=True)
    pagamento_id = Column(Integer, ForeignKey("pagamentos.id"), nullable=True, index=True)
    status = Column(String, nullable=False, default="pending")
    dados_coletados = Column(Text, nullable=True)
    itens_pendentes = Column(Text, nullable=True)
    ultimo_followup_em = Column(DateTime, nullable=True)
    proximo_followup_em = Column(DateTime, nullable=True)
    prazo_conclusao_em = Column(DateTime, nullable=True)
    concluido_em = Column(DateTime, nullable=True)
    criado_em = Column(DateTime, nullable=True)
    atualizado_em = Column(DateTime, nullable=True)

    tenant = relationship("Tenant")
    nutricionista = relationship("Nutricionista")
    cliente = relationship("Cliente")
    agenda_evento = relationship("AgendaEvento")
    pagamento = relationship("Pagamento")
