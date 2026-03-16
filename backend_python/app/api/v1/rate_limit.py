from fastapi import APIRouter, Depends, HTTPException
from app.workers.redis_worker import get_cache, set_cache

router = APIRouter()

@router.post("/rate_limit/check")
def check_rate_limit(user_id: str):
    key = f"rate:{user_id}"
    count = get_cache(key)
    if count and int(count) > 100:
        raise HTTPException(status_code=429, detail="Limite de requisições atingido")
    set_cache(key, str(int(count or 0) + 1), expire=60)
    return {"status": "ok", "count": int(count or 0) + 1}