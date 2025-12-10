from fastapi import APIRouter, Depends, Query
from datetime import date, timedelta
from sqlmodel import Session
from app.core.database import get_session
from app.services.room_service import RoomService
from app.schemas.room import RoomRead

router = APIRouter(prefix="/rooms", tags=["Rooms"])

@router.get("/room-types/{room_type_id}/available-rooms", response_model=list[RoomRead])
def get_available_rooms(
    room_type_id: int,
    checkin: date = Query(
        default=None,
        example=str(date.today()),
        description="Ngày nhận phòng (YYYY-MM-DD)"
    ),
    checkout: date = Query(
        default=None,
        example=str(date.today() + timedelta(days=1)),
        description="Ngày trả phòng (YYYY-MM-DD)"
    ),
    session: Session = Depends(get_session)
):
    # Auto default nếu FE không truyền
    if checkin is None:
        checkin = date.today()
    if checkout is None:
        checkout = checkin + timedelta(days=1)

    return RoomService.get_available_rooms(
        session=session,
        room_type_id=room_type_id,
        checkin=checkin,
        checkout=checkout,
    )
