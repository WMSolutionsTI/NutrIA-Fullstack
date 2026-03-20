from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.domain.models.base import Base

class Arquivo(Base):
    __tablename__ = "arquivos"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    tipo = Column(String, nullable=False)  # Ex: "imagem", "audio", "video", "documento"
    caminho_s3 = Column(String, nullable=False)  # Path no Minio/S3
    tamanho = Column(Integer)
    criado_em = Column(DateTime)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=True)
    tenant = relationship("Tenant")
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=True)
    cliente = relationship("Cliente")
    conversa_id = Column(Integer, ForeignKey("conversas.id"), nullable=True)
    conversa = relationship("Conversa")