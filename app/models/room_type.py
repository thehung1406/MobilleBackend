from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .property import Property
    from .room import Room


class RoomType(SQLModel, table=True):
    __tablename__ = "room_type"

    id: Optional[int] = Field(default=None, primary_key=True)
    property_id: int = Field(foreign_key="property.id", index=True)

    name: str
    price: int
    max_occupancy: int
    is_active: bool = True

    property: "Property" = Relationship(back_populates="room_types")
    rooms: List["Room"] = Relationship(back_populates="room_type")
