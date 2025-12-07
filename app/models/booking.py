from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from datetime import date

from app.models import User, Payment
from app.models.booked_room import BookedRoom


class Booking(SQLModel, table=True):
    __tablename__ = "booking"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")

    booking_date: date

    user: "User" = Relationship(back_populates="bookings")
    booked_rooms: List["BookedRoom"] = Relationship(back_populates="booking")
    payment: Optional["Payment"] = Relationship(back_populates="booking")
