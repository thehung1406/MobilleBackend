# app/routers/booking.py
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.worker.tasks import process_booking_task
from app.schemas.booking import BookingCreate
from app.schemas.common import TaskResponse   # 👉 thêm response model chuẩn
from app.utils.dependencies import get_current_user
from app.core.database import get_session

router = APIRouter(prefix="/booking", tags=["Booking"])


@router.post("", response_model=TaskResponse)
def create_booking(
    payload: BookingCreate,
    user=Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    SUBMIT BOOKING REQUEST
    ------------------------
    - Validate minimum logic
    - Push vào Celery queue
    - Worker xử lý async
    """
    # Optional: Check nếu user bị inactive
    if not user.is_active:
        raise HTTPException(403, "User is inactive")

    # Convert schema → dict cho Celery
    data = payload.model_dump()
    data["user_id"] = user.id

    # Push vào queue
    task = process_booking_task.delay(data)

    return TaskResponse(
        message="Booking is being processed",
        task_id=task.id,
        status="queued"
    )
