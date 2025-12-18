import redis
from app.core.config import settings

r = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=2,
    decode_responses=True
)

LOCK_EXPIRE = 60 * 15  # fail-safe

def make_lock_key(room_id: int, checkin, checkout):
    return f"lock:room:{room_id}:{checkin}:{checkout}"

def acquire_room_lock(room_id: int, checkin, checkout) -> bool:
    key = make_lock_key(room_id, checkin, checkout)
    return r.set(key, "1", nx=True, ex=LOCK_EXPIRE)

def release_room_lock(room_id: int, checkin, checkout):
    key = make_lock_key(room_id, checkin, checkout)
    r.delete(key)
