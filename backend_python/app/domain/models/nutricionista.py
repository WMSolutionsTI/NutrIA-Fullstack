from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.domain.models.base import Base


class Nutricionista(Base):
    __tablename__ = "nutricionistas"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    status = Column(String, default="active")
    plano = Column(String, nullable=False)
    tenant_id = Column(Integer, ForeignKey("tenants.id"))
    tenant = relationship("Tenant", back_populates="nutricionistas")
    caixas_de_entrada = relationship("CaixaDeEntrada", back_populates="nutricionista")
    permissoes = Column(String)  # JSON string or dict
    auditoria = Column(String)
    tipo_user = Column(String, default="nutri")  # 'admin', 'nutri', 'secretaria'

    @property
    def papel(self) -> str:
        return self.tipo_user or "nutri"

    @papel.setter
    def papel(self, value: str) -> None:
        self.tipo_user = value

    @property
    def contexto_ia(self) -> str | None:
        return self.auditoria

    @contexto_ia.setter
    def contexto_ia(self, value: str | None) -> None:
        self.auditoria = value
