from celery import Celery
from celery.schedules import crontab
from app.core.config import settings


# ---------------------------------------------------------
# Celery Configuration
# ---------------------------------------------------------

celery_app = Celery(
    "booking_system",
    broker=settings.REDIS_URL,     # Redis as broker
    backend=settings.REDIS_URL,    # Redis as result backend
)

# Auto-discover tasks in the worker/tasks.py file
celery_app.autodiscover_tasks(["app.worker"])


# ---------------------------------------------------------
# Celery Beat — For Scheduled Tasks (Optional)
# Example jobs:
#   - Auto unlock rooms at 00:00
#   - Auto send daily summary
# ---------------------------------------------------------

celery_app.conf.beat_schedule = {
    "unlock-rooms-every-5-minutes": {
        "task": "app.worker.tasks.unlock_expired_rooms",
        "schedule": 300,   # every 5 minutes
    },
}

celery_app.conf.timezone = "Asia/Ho_Chi_Minh"


# ---------------------------------------------------------
# Optional Celery tuning
# ---------------------------------------------------------

celery_app.conf.update(
    task_track_started=True,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    broker_connection_retry_on_startup=True,
)

