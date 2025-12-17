from pydantic import BaseModel
from datetime import date, datetime
from typing import List, Optional


class BookingCreate(BaseModel):
    room_ids: List[int]
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
    status: str
    selected_rooms: List[int]
    expires_at: Optional[datetime]
    booked_rooms: List[BookedRoomRead]

    class Config:
        from_attributes = True
