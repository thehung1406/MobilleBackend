from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.core.database import get_session
from app.schemas.booking import BookingCreate, BookingRead
from app.services.booking_service import BookingService
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/booking", tags=["Booking"])


@router.post("")
def create_booking(payload: BookingCreate,
                   session: Session = Depends(get_session),
                   user=Depends(get_current_user)):
    return BookingService.create_booking(session, user.id, payload)



@router.get("/my")
def get_my_bookings(session: Session = Depends(get_session),
                    user=Depends(get_current_user)):
    return BookingService.get_my_bookings(session, user.id)


@router.post("/{booking_id}/cancel")
def cancel_booking(booking_id: int,
                   session: Session = Depends(get_session),
                   user=Depends(get_current_user)):
    return BookingService.cancel_booking(session, booking_id, user.id)
