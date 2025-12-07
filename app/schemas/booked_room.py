from datetime import date

from pydantic import BaseModel
from typing import Optional


class BookedRoomBase(BaseModel):
    booking_id: int
    room_id: int
    checkin: date
    checkout: date
    price: int


class BookedRoomCreate(BookedRoomBase):
    pass


class BookedRoomRead(BookedRoomBase):
    id: int

    class Config:
        from_attributes = True
