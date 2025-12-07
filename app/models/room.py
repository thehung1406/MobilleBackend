from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship


class Room(SQLModel, table=True):
    __tablename__ = "room"

    id: Optional[int] = Field(default=None, primary_key=True)

    room_type_id: int = Field(foreign_key="room_type.id", index=True)
    property_id: int = Field(foreign_key="property.id", index=True)

    image: Optional[str] = None
    room_number: str
    is_active: bool = True

    room_type: "RoomType" = Relationship(back_populates="rooms")
    booked_rooms: List["BookedRoom"] = Relationship(back_populates="room")
