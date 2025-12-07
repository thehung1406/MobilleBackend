from fastapi import APIRouter, Depends
from app.worker.tasks import process_booking_task
from app.schemas.booking import BookingCreate
from app.utils.dependencies import get_current_user   # FIX !!!
# from app.core.security import get_current_user  ❌ remove

router = APIRouter(prefix="/booking", tags=["Booking"])


@router.post("")
def create_booking(payload: BookingCreate, user=Depends(get_current_user)):
    """
    Create booking request:
    - Đẩy vào Celery queue
    - Tách xử lý booking sang background worker
    """
    data = payload.model_dump()
    data["user_id"] = user.id

    task = process_booking_task.delay(data)

    return {
        "message": "Booking is being processed",
        "task_id": task.id,
        "status": "pending",
    }
