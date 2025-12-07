from datetime import date, datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship

from app.models.booked_room import BookedRoom
from app.models.payment import Payment


class Booking(SQLModel, table=True):
    __tablename__ = "booking"

    id: Optional[int] = Field(default=None, primary_key=True)

    user_id: int = Field(foreign_key="user.id")
    booking_date: date

    # NEW — số lượng khách trong booking
    num_guests: int = Field(default=1, description="Total number of guests")

    # NEW — trạng thái xử lý booking
    status: str = Field(default="pending", description="pending / paid / cancelled")

    # NEW — hạn giữ phòng (hết hạn -> auto cancel)
    expires_at: Optional[datetime] = Field(
        default=None,
        description="Auto-expire pending booking at this datetime"
    )

    # Relationships
    booked_rooms: List["BookedRoom"] = Relationship(back_populates="booking")
    payment: Optional["Payment"] = Relationship(back_populates="booking")
