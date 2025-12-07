from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship

from app.models import RoomType
from app.models.booked_room import BookedRoom


class Room(SQLModel, table=True):
    __tablename__ = "room"

    id: Optional[int] = Field(default=None, primary_key=True)
    room_type_id: int = Field(foreign_key="room_type.id")

    image: Optional[str] = None
    room_number: str
    is_active: bool = True

    room_type: "RoomType" = Relationship(back_populates="rooms")
    booked_rooms: List["BookedRoom"] = Relationship(back_populates="room")
