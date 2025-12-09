from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import List, Optional


class RoomRequest(BaseModel):
    room_type_id: int
    quantity: int = Field(..., gt=0)


class BookingCreate(BaseModel):
    rooms: List[RoomRequest]
    checkin: date
    checkout: date
    num_guests: int = 1


class BookedRoomRead(BaseModel):
    id: int
    room_id: int
    checkin: date
    checkout: date

    class Config:
        from_attributes = True


class BookingRead(BaseModel):
    id: int
    user_id: int
    booking_date: date
    status: str
    expires_at: Optional[datetime]
    booked_rooms: List[BookedRoomRead]

    class Config:
        from_attributes = True
