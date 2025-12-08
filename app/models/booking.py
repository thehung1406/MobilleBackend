from datetime import date, datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship


class Booking(SQLModel, table=True):
    __tablename__ = "booking"

    id: Optional[int] = Field(default=None, primary_key=True)

    user_id: int = Field(foreign_key="user.id")
    booking_date: date

    num_guests: int = Field(default=1, description="Total number of guests")

    status: str = Field(default="pending", description="pending / paid / cancelled")

    expires_at: Optional[datetime] = Field(
        default=None,
        description="Auto-expire pending booking at this datetime"
    )

    # Relationship
    booked_rooms: List["BookedRoom"] = Relationship(back_populates="booking")
    payment: Optional["Payment"] = Relationship(back_populates="booking")
