from collections.abc import Callable
import os
import time

from fastapi import HTTPException, Request
import redis
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

_redis_url = os.environ.get("REDIS_URL", "redis://redis:6379/0")
redis_client = redis.Redis.from_url(_redis_url, decode_responses=True)


class RateLimiterMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Identifica o cliente pelo IP
        client_ip = request.client.host
        endpoint = request.url.path

        # Define a chave no Redis
        key = f"rate_limit:{client_ip}:{endpoint}"
        now = time.time()
        window = 60  # 60 segundos

        # Sliding window: remove entradas antigas e conta as novas
        pipe = redis_client.pipeline()
        pipe.zremrangebyscore(key, 0, now - window)  # remove antigas
        pipe.zadd(key, {str(now): now})  # adiciona atual
        pipe.zcard(key)  # conta total
        pipe.expire(key, window)  # TTL
        results = pipe.execute()

        request_count = results[2]

        # Verifica limite conforme endpoint
        limit = self.get_limit(endpoint)
        if request_count > limit:
            raise HTTPException(
                status_code=429,
                detail="Too Many Requests",
                headers={"Retry-After": "60"},
            )

        return await call_next(request)

    def get_limit(self, endpoint: str) -> int:
        if "/auth" in endpoint:
            return 10  # 10 req/min para auth
        elif "/webhook" in endpoint:
            return 1000  # 1000 req/min para webhooks
        else:
            return 100  # 100 req/min padrão
