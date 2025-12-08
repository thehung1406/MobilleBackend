from datetime import date
from pydantic import BaseModel
from typing import Optional


# -------------------------
# BASE (nội bộ, không expose)
# -------------------------
class BookedRoomBase(BaseModel):
    room_id: int
    checkin: date
    checkout: date
    price: float   # dùng float cho giá


# -------------------------
# CREATE (chỉ service dùng)
# Client KHÔNG gọi API để tạo booked_room trực tiếp.
# -------------------------
class BookedRoomCreate(BookedRoomBase):
    booking_id: int   # BE sẽ truyền vào, không phải client
    pass


# -------------------------
# READ (trả ra FE)
# -------------------------
class BookedRoomRead(BookedRoomBase):
    id: int
    booking_id: int

    class Config:
        from_attributes = True
