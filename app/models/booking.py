from typing import Optional, List, TYPE_CHECKING
from datetime import date, datetime
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .user import User
    from .booked_room import BookedRoom
    from .payment import Payment


class Booking(SQLModel, table=True):
    __tablename__ = "booking"

    id: Optional[int] = Field(default=None, primary_key=True)

    user_id: int = Field(foreign_key="user.id")
    booking_date: date
    num_guests: int = Field(default=1)
    status: str = Field(default="pending")
    expires_at: Optional[datetime] = None

    # RELATIONS
    user: "User" = Relationship(back_populates="bookings")
    booked_rooms: List["BookedRoom"] = Relationship(back_populates="booking")
    payment: Optional["Payment"] = Relationship(back_populates="booking")
