import os
from datetime import datetime
import json
from typing import Any

import requests
from app.services.crypto_service import decrypt_text, encrypt_text


class AsaasError(Exception):
    pass


def _default_api_url() -> str:
    return os.getenv("ASAAS_API_URL", "https://api-sandbox.asaas.com/v3").rstrip("/")


def _default_api_key() -> str:
    return os.getenv("ASAAS_API_KEY", "").strip()


def _default_timeout() -> int:
    return int(os.getenv("ASAAS_TIMEOUT_SECONDS", "20") or "20")


def _enabled(api_key: str | None = None) -> bool:
    key = (api_key or "").strip()
    if not key:
        key = _default_api_key()
    return bool(key and key != "your_asaas_key")


def is_configured(config: dict[str, Any] | None = None) -> bool:
    if config and config.get("api_key"):
        return _enabled(str(config.get("api_key")))
    return _enabled()


def _headers(api_key: str | None = None) -> dict[str, str]:
    return {
        "Content-Type": "application/json",
        "accept": "application/json",
        "access_token": (api_key or _default_api_key()).strip(),
    }


def _request(
    method: str,
    path: str,
    payload: dict[str, Any] | None = None,
    *,
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    api_key = (config or {}).get("api_key")
    api_url = str((config or {}).get("api_url") or _default_api_url()).rstrip("/")
    timeout = int((config or {}).get("timeout_seconds") or _default_timeout())
    if not _enabled(api_key):
        raise AsaasError("Asaas não configurado.")
    url = f"{api_url}{path}"
    response = requests.request(method, url, headers=_headers(api_key), json=payload, timeout=timeout)
    data = response.json() if response.content else {}
    if response.status_code >= 400:
        errors = data.get("errors") if isinstance(data, dict) else None
        if errors and isinstance(errors, list):
            msg = "; ".join(str(item.get("description", "")).strip() for item in errors if isinstance(item, dict)) or "Erro Asaas"
        else:
            msg = f"Erro Asaas HTTP {response.status_code}"
        raise AsaasError(msg)
    return data if isinstance(data, dict) else {}


def create_customer(
    *,
    nome: str,
    external_reference: str,
    email: str | None = None,
    cpf_cnpj: str | None = None,
    mobile_phone: str | None = None,
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "name": nome[:100],
        "externalReference": external_reference[:60],
    }
    if email:
        payload["email"] = email[:150]
    if cpf_cnpj:
        payload["cpfCnpj"] = cpf_cnpj[:20]
    if mobile_phone:
        payload["mobilePhone"] = mobile_phone[:20]
    return _request("POST", "/customers", payload, config=config)


def create_payment(
    *,
    customer_id: str,
    value: float,
    billing_type: str,
    description: str,
    external_reference: str,
    due_date: str | None = None,
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if not due_date:
        due_date = datetime.utcnow().date().isoformat()
    payload = {
        "customer": customer_id,
        "value": round(float(value), 2),
        "billingType": billing_type,
        "dueDate": due_date,
        "description": description[:500],
        "externalReference": external_reference[:80],
    }
    return _request("POST", "/payments", payload, config=config)


def get_balance(*, config: dict[str, Any] | None = None) -> dict[str, Any]:
    return _request("GET", "/finance/balance", config=config)


def load_asaas_config_from_user(user) -> dict[str, Any]:
    raw = getattr(user, "permissoes", None)
    if not raw:
        return {}
    metadata = {}
    if isinstance(raw, dict):
        metadata = raw
    else:
        try:
            metadata = json.loads(raw)
        except Exception:
            metadata = {}
    if not isinstance(metadata, dict):
        return {}

    integrations = metadata.get("integrations")
    if not isinstance(integrations, dict):
        return {}
    asaas = integrations.get("asaas")
    if not isinstance(asaas, dict):
        return {}
    encrypted_key = str(asaas.get("api_key_encrypted") or "").strip()
    api_key = decrypt_text(encrypted_key) if encrypted_key else ""
    return {
        "api_key": api_key,
        "api_url": str(asaas.get("api_url") or _default_api_url()).rstrip("/"),
        "webhook_token": str(asaas.get("webhook_token") or "").strip(),
        "wallet_id": str(asaas.get("wallet_id") or "").strip(),
        "timeout_seconds": _default_timeout(),
    }


def save_asaas_config_to_user(
    user,
    *,
    api_key: str,
    api_url: str | None = None,
    webhook_token: str | None = None,
    wallet_id: str | None = None,
) -> dict[str, Any]:
    raw = getattr(user, "permissoes", None)
    metadata = {}
    if isinstance(raw, dict):
        metadata = raw
    elif isinstance(raw, str) and raw.strip():
        try:
            metadata = json.loads(raw)
        except Exception:
            metadata = {}
    if not isinstance(metadata, dict):
        metadata = {}
    integrations = metadata.get("integrations")
    if not isinstance(integrations, dict):
        integrations = {}
    integrations["asaas"] = {
        "api_key_encrypted": encrypt_text(api_key.strip()),
        "api_url": (api_url or _default_api_url()).rstrip("/"),
        "webhook_token": (webhook_token or "").strip(),
        "wallet_id": (wallet_id or "").strip(),
        "updated_at": datetime.utcnow().isoformat(),
    }
    metadata["integrations"] = integrations
    metadata["asaas_configurada"] = True
    user.permissoes = json.dumps(metadata, ensure_ascii=False)
    return metadata
