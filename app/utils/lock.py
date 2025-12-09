import redis
import time
from app.core.config import settings

r = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=2,
    decode_responses=True
)

LOCK_EXPIRE = 60 * 15  # 15 phút


def acquire_room_lock(room_id: int) -> bool:
    key = f"lock:room:{room_id}"
    return r.set(key, "1", nx=True, ex=LOCK_EXPIRE)


def release_room_lock(room_id: int):
    r.delete(f"lock:room:{room_id}")
