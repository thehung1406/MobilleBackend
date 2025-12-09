# app/schemas/booked_room.py
from datetime import date
from pydantic import BaseModel, Field
from typing import Optional


# -------------------------
# BASE (internal)
# -------------------------
class BookedRoomBase(BaseModel):
    room_id: int
    checkin: date
    checkout: date


# -------------------------
# CREATE (BE dùng, không expose client)
# -------------------------
class BookedRoomCreate(BookedRoomBase):
    booking_id: int


# -------------------------
# READ (return to FE)
# -------------------------
class BookedRoomRead(BaseModel):
    id: int
    booking_id: int
    room_id: int
    checkin: date
    checkout: date


    class Config:
        from_attributes = True
