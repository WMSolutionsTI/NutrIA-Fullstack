import redis
import os

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, password=REDIS_PASSWORD)

def set_cache(key: str, value: str, expire: int = 3600):
    redis_client.set(key, value, ex=expire)

def get_cache(key: str):
    return redis_client.get(key)

def delete_cache(key: str):
    redis_client.delete(key)


def set_if_not_exists(key: str, value: str, expire: int = 3600) -> bool:
    return bool(redis_client.set(key, value, ex=expire, nx=True))
