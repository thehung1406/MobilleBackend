# đảm bảo Celery autodiscover load tasks
from app.worker.tasks import cleanup_expired_bookings  # noqa: F401
