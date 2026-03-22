from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.domain.models.base import Base


class GoogleCalendarIntegration(Base):
    __tablename__ = "google_calendar_integrations"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    nutricionista_id = Column(Integer, ForeignKey("nutricionistas.id"), nullable=False, unique=True, index=True)
    google_email = Column(String, nullable=True)
    calendar_id = Column(String, nullable=False, default="primary")
    access_token_encrypted = Column(String, nullable=False)
    refresh_token_encrypted = Column(String, nullable=False)
    token_expires_at = Column(DateTime, nullable=True)
    status = Column(String, nullable=False, default="active")
    criado_em = Column(DateTime, nullable=True)
    atualizado_em = Column(DateTime, nullable=True)

    tenant = relationship("Tenant")
    nutricionista = relationship("Nutricionista")
