import json
import hashlib
import redis
from redis.exceptions import ConnectionError
from app.core.config import settings

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



def make_key(prefix: str, payload: dict):

    serialized = json.dumps(payload, sort_keys=True)
    hashed = hashlib.md5(serialized.encode()).hexdigest()
    return f"{prefix}:{hashed}"



def cache_get(key: str):
    if not r:
        return None

    try:
        raw = r.get(key)
        if raw:
            return json.loads(raw)
        return None
    except ConnectionError:
        return None



def cache_set(key: str, value: dict, expire_seconds: int = 30):
    if not r:
        return False

    def default_serializer(obj):

        if hasattr(obj, "model_dump"):
            return obj.model_dump()

        if hasattr(obj, "dict"):
            return obj.dict()
        return str(obj)

    try:
        r.set(key, json.dumps(value, default=default_serializer), ex=expire_seconds)
        return True
    except ConnectionError:
        return False

