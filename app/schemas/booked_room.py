# app/schemas/booked_room.py
from datetime import date
from pydantic import BaseModel, Field
from typing import Optional



class BookedRoomBase(BaseModel):
    room_id: int
    checkin: date
    checkout: date



class BookedRoomCreate(BookedRoomBase):
    booking_id: int



class BookedRoomRead(BaseModel):
    id: int
    booking_id: int
    room_id: int
    checkin: date
    checkout: date


    class Config:
        from_attributes = True
