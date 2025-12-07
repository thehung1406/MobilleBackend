from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, date
from app.utils.enums import BookingStatus


# -----------------------------
# REQUEST: Client → API
# -----------------------------
class BookingCreate(BaseModel):
    room_ids: List[int] = Field(..., description="List phòng muốn đặt")
    checkin: date
    checkout: date
    num_guests: int = Field(..., description="Số lượng khách")
    price: float = Field(..., description="Tổng tiền hoặc giá theo ngày")


# -----------------------------
# RESPONSE: BookedRoom
# -----------------------------
class BookedRoomRead(BaseModel):
    room_id: int
    checkin: date
    checkout: date
    price: float

    class Config:
        from_attributes = True


# -----------------------------
# RESPONSE: Booking
# -----------------------------
class BookingRead(BaseModel):
    id: int
    user_id: int
    booking_date: date
    status: BookingStatus
    expires_at: Optional[datetime]
    booked_rooms: List[BookedRoomRead]

    class Config:
        from_attributes = True


# -----------------------------
# UPDATE STATUS
# -----------------------------
class BookingStatusUpdate(BaseModel):
    status: BookingStatus  # dùng enum chuẩn
