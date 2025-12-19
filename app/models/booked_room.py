from typing import Optional, TYPE_CHECKING
from datetime import date
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .booking import Booking
    from .room import Room


class BookedRoom(SQLModel, table=True):
    __tablename__ = "booked_room"

    id: Optional[int] = Field(default=None, primary_key=True)

    booking_id: int = Field(foreign_key="booking.id")
    room_id: int = Field(foreign_key="room.id")


    checkin: date
    checkout: date


    booking: "Booking" = Relationship(back_populates="booked_rooms")
    room: "Room" = Relationship(back_populates="booked_rooms")
