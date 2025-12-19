from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .room_type import RoomType
    from .booked_room import BookedRoom


class Room(SQLModel, table=True):
    __tablename__ = "room"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    is_active: bool = True
    image: Optional[str] = None
    room_type_id: int = Field(foreign_key="room_type.id")

    room_type: "RoomType" = Relationship(back_populates="rooms")
    booked_rooms: List["BookedRoom"] = Relationship(back_populates="room")