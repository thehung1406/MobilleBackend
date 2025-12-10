from celery import Celery
from celery.schedules import crontab
from app.core.config import settings

# ---------------------------------------------------------
# Celery App
# ---------------------------------------------------------

celery_app = Celery(
    "booking_system",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

# Auto-discover tasks
celery_app.autodiscover_tasks(["app.worker"])


# ---------------------------------------------------------
# Celery Beat Schedule
# ---------------------------------------------------------
celery_app.conf.beat_schedule = {
    "cleanup-expired-bookings-every-5-minutes": {
        "task": "cleanup_expired_bookings",
        "schedule": 300,  # 5 phút
    },
}

celery_app.conf.timezone = "Asia/Ho_Chi_Minh"


# ---------------------------------------------------------
# Optional tuning
# ---------------------------------------------------------
celery_app.conf.update(
    task_track_started=True,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    broker_connection_retry_on_startup=True,
)
