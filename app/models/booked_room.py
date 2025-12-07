from typing import Optional
from sqlmodel import SQLModel, Field, Relationship


class BookedRoom(SQLModel, table=True):
    __tablename__ = "booked_room"

    id: Optional[int] = Field(default=None, primary_key=True)

    room_id: int = Field(foreign_key="room.id", index=True)
    booking_id: int = Field(foreign_key="booking.id", index=True)

    checkin: str
    checkout: str
    price: int

    room: "Room" = Relationship(back_populates="booked_rooms")
    booking: "Booking" = Relationship(back_populates="booked_rooms")
