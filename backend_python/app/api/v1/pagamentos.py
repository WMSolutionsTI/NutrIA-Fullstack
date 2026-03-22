import os
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.db import get_db
from app.domain.models.contabilidade import Contabilidade
from app.domain.models.nutricionista import Nutricionista
from app.domain.models.pagamento import Pagamento
from app.domain.models.saas_signup_request import SaasSignupRequest
from app.services.anamnese_service import handle_payment_confirmed_for_anamnese
from app.services.asaas_service import load_asaas_config_from_user

router = APIRouter(prefix="/pagamentos", tags=["Pagamentos"])


def _map_status(status: str) -> str:
    normalized = (status or "").upper().strip()
    if normalized in {"RECEIVED", "CONFIRMED", "RECEIVED_IN_CASH"}:
        return "pago"
    if normalized in {"OVERDUE", "REFUNDED", "REFUND_REQUESTED", "CHARGEBACK_DISPUTE"}:
        return "cancelado"
    return "pendente"


@router.post("/asaas/webhook", response_model=dict)
async def asaas_webhook(request: Request, db: Session = Depends(get_db)):
    expected_token = (os.getenv("ASAAS_WEBHOOK_TOKEN") or "").strip()
    received_token = (
        request.headers.get("asaas-access-token")
        or request.headers.get("x-asaas-access-token")
        or ""
    ).strip()
    if expected_token and expected_token != received_token:
        admin = (
            db.query(Nutricionista)
            .filter(Nutricionista.tipo_user == "admin", Nutricionista.status == "active")
            .order_by(Nutricionista.id.asc())
            .first()
        )
        admin_cfg = load_asaas_config_from_user(admin) if admin else {}
        admin_token = str(admin_cfg.get("webhook_token") or "").strip()
        if not admin_token or admin_token != received_token:
            raise HTTPException(status_code=401, detail="Webhook Asaas inválido")
    elif not expected_token:
        admin = (
            db.query(Nutricionista)
            .filter(Nutricionista.tipo_user == "admin", Nutricionista.status == "active")
            .order_by(Nutricionista.id.asc())
            .first()
        )
        admin_cfg = load_asaas_config_from_user(admin) if admin else {}
        admin_token = str(admin_cfg.get("webhook_token") or "").strip()
        if admin_token and admin_token != received_token:
            raise HTTPException(status_code=401, detail="Webhook Asaas inválido")

    payload = await request.json()
    payment_data = payload.get("payment") or payload.get("data") or {}
    if not isinstance(payment_data, dict):
        raise HTTPException(status_code=400, detail="Payload inválido")

    payment_id = str(payment_data.get("id") or "").strip()
    if not payment_id:
        raise HTTPException(status_code=400, detail="payment.id ausente")

    status_asaas = str(payment_data.get("status") or "").strip()
    mapped_status = _map_status(status_asaas)

    pagamento = (
        db.query(Pagamento)
        .filter(Pagamento.referencia == payment_id)
        .order_by(Pagamento.id.desc())
        .first()
    )
    if not pagamento:
        signup = (
            db.query(SaasSignupRequest)
            .filter(SaasSignupRequest.asaas_payment_id == payment_id)
            .order_by(SaasSignupRequest.id.desc())
            .first()
        )
        if not signup:
            return {"status": "ignored_not_found", "payment_id": payment_id}
        signup.payment_status = mapped_status
        signup.atualizado_em = datetime.now(UTC)
        db.add(signup)
        if mapped_status == "pago" and not signup.provisioned_nutricionista_id:
            from app.api.v1.onboarding import _provisionar_nutri
            from app.workers.cadastro_assinatura_worker import enviar_email_boas_vindas_assinatura

            existente = db.query(Nutricionista).filter(Nutricionista.email == signup.email).first()
            if not existente:
                tenant, nutricionista, conta_chatwoot, senha_temporaria = _provisionar_nutri(
                    db=db,
                    nome=signup.nome,
                    email=signup.email,
                    plano_nome=signup.plano_nome,
                    auditoria_tag=f"assinatura_confirmada:{signup.asaas_payment_id}",
                    telefone=signup.telefone,
                )
                enviar_email_boas_vindas_assinatura(
                    email=signup.email,
                    nome=signup.nome,
                    senha_temporaria=senha_temporaria,
                    plano=signup.plano_nome,
                    limite_inboxes=conta_chatwoot.limite_inboxes_base + conta_chatwoot.inboxes_extra,
                )
                signup.provisioned_tenant_id = tenant.id
                signup.provisioned_nutricionista_id = nutricionista.id
                signup.provisioned_chatwoot_account = conta_chatwoot.chatwoot_account_id
                signup.provisioned_em = datetime.now(UTC)
                db.add(signup)
        db.commit()
        return {"status": "ok", "payment_id": payment_id, "payment_status": mapped_status, "scope": "saas_signup"}

    pagamento.status = mapped_status
    if mapped_status == "pago":
        pagamento.data_pagamento = datetime.now(UTC).replace(tzinfo=None)
    db.add(pagamento)

    lancamento = (
        db.query(Contabilidade)
        .filter(Contabilidade.assas_id == payment_id)
        .order_by(Contabilidade.id.desc())
        .first()
    )
    if lancamento:
        lancamento.status = mapped_status
        db.add(lancamento)

    db.commit()

    if mapped_status == "pago":
        try:
            handle_payment_confirmed_for_anamnese(db, pagamento)
        except Exception:
            # Não escalar para admin: este webhook é de contexto de cliente.
            pass
    return {"status": "ok", "payment_id": payment_id, "payment_status": mapped_status}
