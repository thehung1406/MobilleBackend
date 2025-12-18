from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "booking_system",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

# Auto-discover tasks (QUAN TRỌNG)
celery_app.autodiscover_tasks(["app.worker"])

# Beat schedule
celery_app.conf.beat_schedule = {
    "cleanup-expired-bookings-every-30-seconds": {
        "task": "cleanup_expired_bookings",
        "schedule": 30,
    },
}

celery_app.conf.timezone = "Asia/Ho_Chi_Minh"

celery_app.conf.update(
    task_track_started=True,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    broker_connection_retry_on_startup=True,
)
