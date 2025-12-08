from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship

class Room(SQLModel, table=True):
    __tablename__ = "room"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str

    # relationship
    booked_rooms: List["BookedRoom"] = Relationship(back_populates="room")
