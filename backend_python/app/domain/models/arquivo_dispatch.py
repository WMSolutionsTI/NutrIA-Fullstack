from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.domain.models.base import Base


class ArquivoDispatch(Base):
    __tablename__ = "arquivo_dispatches"

    id = Column(Integer, primary_key=True, index=True)
    arquivo_id = Column(Integer, ForeignKey("arquivos.id"), nullable=False, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    nutricionista_id = Column(Integer, ForeignKey("nutricionistas.id"), nullable=False, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=True, index=True)
    caixa_id = Column(Integer, ForeignKey("caixas_de_entrada.id"), nullable=True, index=True)
    account_id = Column(String, nullable=True)
    conversation_id = Column(String, nullable=True)
    mime_type = Column(String, nullable=True)
    sha256 = Column(String, nullable=True)
    status = Column(String, nullable=False, default="queued")
    tentativas = Column(Integer, nullable=False, default=0)
    erro = Column(Text, nullable=True)
    criado_em = Column(DateTime, nullable=True)
    atualizado_em = Column(DateTime, nullable=True)

    arquivo = relationship("Arquivo")
    tenant = relationship("Tenant")
    nutricionista = relationship("Nutricionista")
    cliente = relationship("Cliente")
    caixa = relationship("CaixaDeEntrada")
