from datetime import UTC, datetime, timedelta
import os

from fastapi import APIRouter, Depends, HTTPException
from jose import JWTError, jwt
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.v1.auth import ALGORITHM, SECRET_KEY, get_current_user
from app.db import get_db
from app.domain.models.google_calendar_integration import GoogleCalendarIntegration
from app.domain.models.nutricionista import Nutricionista
from app.services.crypto_service import decrypt_text, encrypt_text
from app.services.google_calendar_service import (
    build_google_consent_url,
    exchange_code_for_token,
    fetch_google_profile,
    refresh_access_token,
    token_expiration,
)

router = APIRouter(prefix="/integracoes/google", tags=["Integrações Google"])


class IniciarIntegracaoGoogleResponse(BaseModel):
    auth_url: str
    state: str


def _build_state_token(nutri: Nutricionista) -> str:
    exp = datetime.now(UTC) + timedelta(minutes=15)
    payload = {
        "sub": nutri.email,
        "nutricionista_id": nutri.id,
        "tenant_id": nutri.tenant_id,
        "type": "google_oauth_state",
        "exp": exp,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def _parse_state_token(state: str) -> dict:
    try:
        payload = jwt.decode(state, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "google_oauth_state":
            raise HTTPException(status_code=400, detail="State inválido")
        return payload
    except JWTError as exc:
        raise HTTPException(status_code=400, detail="State inválido ou expirado") from exc


@router.post("/iniciar", response_model=IniciarIntegracaoGoogleResponse)
def iniciar_integracao_google(
    current_user: Nutricionista = Depends(get_current_user),
):
    if not os.getenv("GOOGLE_CLIENT_ID") or not os.getenv("GOOGLE_CLIENT_SECRET"):
        raise HTTPException(status_code=400, detail="Integração Google não configurada no servidor")
    state_token = _build_state_token(current_user)
    return {"auth_url": build_google_consent_url(state_token), "state": state_token}


@router.get("/callback", response_model=dict)
def callback_integracao_google(
    code: str,
    state: str,
    db: Session = Depends(get_db),
):
    state_payload = _parse_state_token(state)
    nutricionista_id = int(state_payload["nutricionista_id"])
    nutri = db.query(Nutricionista).filter(Nutricionista.id == nutricionista_id).first()
    if not nutri:
        raise HTTPException(status_code=404, detail="Nutricionista não encontrada para callback")

    token_data = exchange_code_for_token(code)
    access_token = token_data.get("access_token")
    refresh_token_value = token_data.get("refresh_token")
    if not access_token or not refresh_token_value:
        raise HTTPException(status_code=400, detail="Google não retornou tokens de integração válidos")

    profile = fetch_google_profile(access_token)
    integration = (
        db.query(GoogleCalendarIntegration)
        .filter(GoogleCalendarIntegration.nutricionista_id == nutri.id)
        .first()
    )
    if not integration:
        integration = GoogleCalendarIntegration(
            tenant_id=nutri.tenant_id,
            nutricionista_id=nutri.id,
            criado_em=datetime.utcnow(),
        )
    integration.google_email = profile.get("email")
    integration.calendar_id = "primary"
    integration.access_token_encrypted = encrypt_text(access_token)
    integration.refresh_token_encrypted = encrypt_text(refresh_token_value)
    integration.token_expires_at = token_expiration(token_data.get("expires_in"))
    integration.status = "active"
    integration.atualizado_em = datetime.utcnow()

    db.add(integration)
    db.commit()
    db.refresh(integration)
    return {"status": "google_conectado", "google_email": integration.google_email, "calendar_id": integration.calendar_id}


@router.get("/status", response_model=dict)
def status_integracao_google(
    current_user: Nutricionista = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    integration = (
        db.query(GoogleCalendarIntegration)
        .filter(GoogleCalendarIntegration.nutricionista_id == current_user.id)
        .first()
    )
    if not integration:
        return {"conectado": False}
    return {
        "conectado": integration.status == "active",
        "google_email": integration.google_email,
        "calendar_id": integration.calendar_id,
        "expira_em": integration.token_expires_at.isoformat() if integration.token_expires_at else None,
    }


@router.post("/desconectar", response_model=dict)
def desconectar_integracao_google(
    current_user: Nutricionista = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    integration = (
        db.query(GoogleCalendarIntegration)
        .filter(GoogleCalendarIntegration.nutricionista_id == current_user.id)
        .first()
    )
    if not integration:
        return {"status": "ja_desconectado"}

    integration.status = "revoked"
    integration.access_token_encrypted = encrypt_text("")
    integration.refresh_token_encrypted = encrypt_text("")
    integration.atualizado_em = datetime.utcnow()
    db.add(integration)
    db.commit()
    return {"status": "google_desconectado"}


def get_valid_google_access_token(db: Session, integration: GoogleCalendarIntegration) -> str:
    if integration.token_expires_at and integration.token_expires_at.tzinfo is None:
        expires_at = integration.token_expires_at.replace(tzinfo=UTC)
    else:
        expires_at = integration.token_expires_at

    if expires_at and datetime.now(UTC) < expires_at - timedelta(minutes=1):
        return decrypt_text(integration.access_token_encrypted)

    refresh_token_value = decrypt_text(integration.refresh_token_encrypted)
    refreshed = refresh_access_token(refresh_token_value)
    access_token = refreshed.get("access_token")
    if not access_token:
        raise HTTPException(status_code=400, detail="Não foi possível renovar token Google")
    integration.access_token_encrypted = encrypt_text(access_token)
    integration.refresh_token_encrypted = encrypt_text(refreshed.get("refresh_token", refresh_token_value))
    integration.token_expires_at = token_expiration(refreshed.get("expires_in"))
    integration.atualizado_em = datetime.utcnow()
    db.add(integration)
    db.commit()
    return access_token
