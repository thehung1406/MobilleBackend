import json
import hashlib
import redis
from app.core.config import settings

# DB=1 để tách biệt với lock hoặc task queue
r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=1)


def make_key(prefix: str, payload: dict):
    serialized = json.dumps(payload, sort_keys=True)
    hashed = hashlib.md5(serialized.encode()).hexdigest()
    return f"{prefix}:{hashed}"


def cache_get(key: str):
    data = r.get(key)
    if data:
        return json.loads(data)
    return None


def cache_set(key: str, value: dict, expire_seconds: int = 30):
    r.set(key, json.dumps(value), ex=expire_seconds)
