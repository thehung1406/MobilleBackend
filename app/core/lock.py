import uuid
import time
import redis
from typing import Optional
from app.core.logger import logger  # nếu bạn có logger riêng


# 👉 Load từ ENV / config
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)


class RedisLock:
    """
    Distributed lock using Redis.
    Prevents two users from booking the same room at the same time.
    """

    def __init__(self, key: str, timeout: int = 5):
        self.key = key
        self.timeout = timeout
        self.value = str(uuid.uuid4())  # unique lock owner

    def acquire(self) -> bool:
        """
        Try to acquire lock until timeout.
        """
        end = time.time() + self.timeout

        while time.time() < end:
            # Try to acquire lock
            acquired = r.set(self.key, self.value, nx=True, ex=self.timeout)
            if acquired:
                return True

            time.sleep(0.05)

        logger.warning(f"[RedisLock] Failed to acquire lock for {self.key}")
        return False

    def try_lock(self) -> bool:
        """Acquire lock only once; no retry."""
        return bool(r.set(self.key, self.value, nx=True, ex=self.timeout))

    def release(self):
        """
        Release lock only if owner matches.
        """
        try:
            if r.get(self.key) == self.value.encode():
                r.delete(self.key)
        except Exception as e:
            logger.error(f"[RedisLock] Release failed: {e}")

    def __enter__(self):
        if not self.acquire():
            raise TimeoutError(f"Could not acquire Redis lock for key {self.key}")
        return self

    def __exit__(self, exc_type, exc, tb):
        self.release()
