
from app.core.redis import redis_main

def is_rate_limited(key: str, limit: int, period: int) -> bool:

    count = redis_main.get(key)
    if count is None:
        # First call, set the TTL and count
        redis_main.setex(key, period, 1)
        return False
    try:
        current = int(count)
    except (TypeError, ValueError):
        redis_main.setex(key, period, 1)
        return False
    if current < limit:
        redis_main.incr(key)
        return False
    return True
