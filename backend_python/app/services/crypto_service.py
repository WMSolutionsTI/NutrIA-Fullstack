import base64
import hashlib
import os

try:
    from cryptography.fernet import Fernet
except Exception:  # pragma: no cover - fallback quando dependência não estiver disponível
    Fernet = None


def _encryption_secret() -> str:
    return os.getenv("TOKEN_ENCRYPTION_SECRET") or os.getenv("JWT_SECRET_KEY", "dev-only-change-me")


def _fernet_key() -> bytes:
    secret = _encryption_secret().encode("utf-8")
    digest = hashlib.sha256(secret).digest()
    return base64.urlsafe_b64encode(digest)


def encrypt_text(plain: str) -> str:
    if not plain:
        return ""
    if Fernet:
        return Fernet(_fernet_key()).encrypt(plain.encode("utf-8")).decode("utf-8")
    # fallback reversível para ambientes mínimos (não recomendado para produção)
    return base64.urlsafe_b64encode(plain.encode("utf-8")).decode("utf-8")


def decrypt_text(cipher: str) -> str:
    if not cipher:
        return ""
    if Fernet:
        return Fernet(_fernet_key()).decrypt(cipher.encode("utf-8")).decode("utf-8")
    return base64.urlsafe_b64decode(cipher.encode("utf-8")).decode("utf-8")
