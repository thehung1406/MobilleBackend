from typing import Optional, List, TYPE_CHECKING
from datetime import date, datetime
from sqlmodel import SQLModel, Field, Relationship, Column, JSON

if TYPE_CHECKING:
    from .user import User
    from .booked_room import BookedRoom
    from .payment import Payment


class Booking(SQLModel, table=True):
    __tablename__ = "booking"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")

    checkin: date
    checkout: date
    booking_date: datetime = Field(default_factory=datetime.utcnow)
    num_guests: int = 1

    status: str = Field(default="pending")
    expires_at: Optional[datetime] = None


    selected_rooms: List[int] = Field(
        default_factory=list,
        sa_column=Column(JSON)
    )

    # RELATIONS
    user: "User" = Relationship(back_populates="bookings")
    booked_rooms: List["BookedRoom"] = Relationship(back_populates="booking")
    payment: Optional["Payment"] = Relationship(back_populates="booking")
