import redis
import os

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)

def set_cache(key: str, value: str, expire: int = 3600):
    redis_client.set(key, value, ex=expire)

def get_cache(key: str):
    return redis_client.get(key)

def delete_cache(key: str):
    redis_client.delete(key)