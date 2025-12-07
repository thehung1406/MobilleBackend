from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship

from app.models import Property, Room


class RoomType(SQLModel, table=True):
    __tablename__ = "room_type"

    id: Optional[int] = Field(default=None, primary_key=True)
    property_id: int = Field(foreign_key="property.id")

    price: int
    name: str
    max_occupancy: int
    is_active: bool = True

    property: "Property" = Relationship(back_populates="room_types")
    rooms: List["Room"] = Relationship(back_populates="room_type")
