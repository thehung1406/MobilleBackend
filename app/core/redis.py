import redis
from app.core.config import settings

# db=0: cache & jwt blacklist
redis_main = redis.Redis.from_url(f"{settings.REDIS_URL}/0", decode_responses=True)

# db=1: celery broker/backend
redis_celery = redis.Redis.from_url(f"{settings.REDIS_URL}/1", decode_responses=True)

# pub/sub cho websocket
redis_pubsub = redis_main.pubsub()

# Helpers
def set_cache(key: str, value: str, ttl: int = 3600):
    redis_main.setex(key, ttl, value)

def get_cache(key: str):
    return redis_main.get(key)

def delete_cache(key: str):
    redis_main.delete(key)

def add_to_blacklist(token: str, ttl: int):
    redis_main.setex(f"blacklist:{token}", ttl, "true")

def is_token_blacklisted(token: str) -> bool:
    return redis_main.exists(f"blacklist:{token}") == 1

def publish_message(channel: str, message: str):
    redis_main.publish(channel, message)
