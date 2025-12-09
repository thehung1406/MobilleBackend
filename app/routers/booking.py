from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.core.database import get_session
from app.schemas.booking import BookingCreate
from app.services.booking_service import BookingService
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/booking", tags=["Booking"])


@router.post("")
def create_booking(payload: BookingCreate,
                   session: Session = Depends(get_session),
                   user=Depends(get_current_user)):

    return BookingService.create_booking(
        session=session,
        user_id=user.id,
        payload=payload
    )
