from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from app.domain.models.base import Base

class Conversa(Base):
    __tablename__ = "conversas"
    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"))
    nutricionista_id = Column(Integer, ForeignKey("nutricionistas.id"))
    caixa_id = Column(Integer, ForeignKey("caixas_de_entrada.id"))
    chatwoot_account_id = Column(String, nullable=True, index=True)
    chatwoot_inbox_id = Column(String, nullable=True, index=True)
    canal_origem = Column(String, nullable=True, index=True)
    chatwoot_conversation_id = Column(String, nullable=True, index=True)
    mensagem = Column(String, nullable=False)
    data = Column(DateTime)
    contexto_ia = Column(String)  # Para prompts/contexto IA
    modo = Column(String, default="ia")  # "ia" ou "direto"
    em_conversa_direta = Column(Boolean, default=False)
    cliente = relationship("Cliente")
    nutricionista = relationship("Nutricionista")
    caixa = relationship("CaixaDeEntrada")
