import os

from fastapi import HTTPException
import redis

_redis_url = os.environ.get("REDIS_URL", "redis://redis:6379/0")
redis_client = redis.Redis.from_url(_redis_url, decode_responses=True)


async def check_lock(key: str, max_attempts: int = 5, lock_ttl: int = 600) -> None:
    """
    Verifica se um usuário/IP está bloqueado por excesso de tentativas.

    - key: identificador único (ex: "login:attempt:192.168.0.1")
    - max_attempts: número máximo de tentativas antes do bloqueio
    - lock_ttl: tempo de bloqueio em segundos (padrão: 10 minutos)
    """
    attempts = redis_client.get(key)

    if attempts and int(attempts) >= max_attempts:
        raise HTTPException(
            status_code=429,
            detail=(
                "Conta temporariamente bloqueada por excesso de tentativas. "
                "Tente novamente em 10 minutos."
            ),
        )
