from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.domain.models.base import Base


class NutriContactVerification(Base):
    __tablename__ = "nutri_contact_verifications"

    id = Column(Integer, primary_key=True, index=True)
    nutricionista_id = Column(Integer, ForeignKey("nutricionistas.id"), nullable=False)
    contato_chatwoot = Column(String, nullable=False, index=True)
    codigo = Column(String, nullable=False)
    status = Column(String, nullable=False, default="pending")
    expiracao_em = Column(DateTime, nullable=False)
    tentativas = Column(Integer, nullable=False, default=0)
    criado_em = Column(DateTime)
    validado_em = Column(DateTime)

    nutricionista = relationship("Nutricionista")
