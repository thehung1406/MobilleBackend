import redis
from app.core.config import settings

# Redis DB2 dành riêng cho lock
r = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=2,
    decode_responses=True
)

LOCK_EXPIRE = 60 * 15  # 15 phút


def make_lock_key(room_id: int, checkin, checkout):
    """
    Lock theo:
      - room_id
      - checkin (YYYY-MM-DD)
      - checkout (YYYY-MM-DD)
    → Người khác đặt ngày khác vẫn OK
    """
    return f"lock:room:{room_id}:{checkin}:{checkout}"


def acquire_room_lock(room_id: int, checkin, checkout) -> bool:
    """Đặt lock, nếu tồn tại → phòng đang có người giữ"""
    key = make_lock_key(room_id, checkin, checkout)
    return r.set(key, "1", nx=True, ex=LOCK_EXPIRE)


def release_room_lock(room_id: int, checkin, checkout):
    """Gỡ lock đúng ngày"""
    key = make_lock_key(room_id, checkin, checkout)
    r.delete(key)
