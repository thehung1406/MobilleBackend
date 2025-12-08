from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .room_type import RoomType
    from .booked_room import BookedRoom


class Room(SQLModel, table=True):
    __tablename__ = "room"

    id: Optional[int] = Field(default=None, primary_key=True)

    name: str
    room_number: Optional[str] = None     # 🆕 hiển thị số phòng
    image: Optional[str] = None           # 🆕 ảnh phòng
    is_active: bool = True                # 🆕 phòng có sử dụng hay không

    room_type_id: int = Field(foreign_key="room_type.id")

    # RELATIONSHIPS
    room_type: "RoomType" = Relationship(back_populates="rooms")
    booked_rooms: List["BookedRoom"] = Relationship(back_populates="room")
