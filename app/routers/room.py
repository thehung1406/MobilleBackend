from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.core.database import get_session
from app.services.room_service import RoomService
from app.schemas.room_availability import RoomAvailabilityResponse,RoomAvailabilityRequest

router = APIRouter(prefix="/rooms", tags=["Rooms"])


@router.post("/{room_id}/availability", response_model=RoomAvailabilityResponse)
def check_availability(room_id: int, payload: RoomAvailabilityRequest, session: Session = Depends(get_session)):
    available = RoomService.check_availability(session, room_id, payload.checkin, payload.checkout)
    return RoomAvailabilityResponse(room_id=room_id, available=available)
