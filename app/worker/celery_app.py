from celery import Celery
from celery.schedules import crontab
from app.core.config import settings

celery = Celery(
    "hotel_tasks",
    broker=f"{settings.REDIS_URL}/1",
    backend=f"{settings.REDIS_URL}/1",
)

celery.conf.update(
    timezone="Asia/Ho_Chi_Minh",
    enable_utc=True,
)

celery.autodiscover_tasks(["app.worker"])
