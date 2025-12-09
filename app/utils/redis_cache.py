import json
import hashlib
import redis
from redis.exceptions import ConnectionError
from app.core.config import settings

# ----------------------------------------------------
# REDIS CLIENT – DB=1 để tách khỏi Celery Worker, Lock
# ----------------------------------------------------
def create_redis_client():
    try:
        client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=1,
            decode_responses=True,  # Không cần .decode('utf-8')
        )
        client.ping()
        print("✅ Redis Cache Connected")
        return client
    except Exception as e:
        print("❌ Redis Cache FAILED:", e)
        return None


r = create_redis_client()


# ----------------------------------------------------
# UTILITY – Tạo cache key (giữ nguyên logic cũ)
# ----------------------------------------------------
def make_key(prefix: str, payload: dict):
    """
    Tạo key dạng: prefix:md5(payload_json)
    => Giữ nguyên để SearchService không bị ảnh hưởng.
    """
    serialized = json.dumps(payload, sort_keys=True)
    hashed = hashlib.md5(serialized.encode()).hexdigest()
    return f"{prefix}:{hashed}"


# ----------------------------------------------------
# CACHE GET – An toàn, không crash API
# ----------------------------------------------------
def cache_get(key: str):
    if not r:
        return None  # fallback mode

    try:
        raw = r.get(key)
        if raw:
            return json.loads(raw)
        return None
    except ConnectionError:
        return None


# ----------------------------------------------------
# CACHE SET – An toàn, mặc định TTL=30s
# ----------------------------------------------------
def cache_set(key: str, value: dict, expire_seconds: int = 30):
    if not r:
        return False  # fallback mode

    def default_serializer(obj):
        # Support Pydantic v2
        if hasattr(obj, "model_dump"):
            return obj.model_dump()
        # Support Pydantic v1
        if hasattr(obj, "dict"):
            return obj.dict()
        return str(obj)

    try:
        r.set(key, json.dumps(value, default=default_serializer), ex=expire_seconds)
        return True
    except ConnectionError:
        return False

