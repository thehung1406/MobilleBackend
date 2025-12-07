from pydantic import BaseModel
from typing import Optional


class RoomBase(BaseModel):
    room_number: str
    image: Optional[str] = None
    is_active: bool = True


class RoomCreate(RoomBase):
    room_type_id: int
    property_id: int


class RoomUpdate(BaseModel):
    room_number: Optional[str] = None
    image: Optional[str] = None
    is_active: Optional[bool] = None


class RoomRead(RoomBase):
    id: int
    room_type_id: int
    property_id: int

    class Config:
        from_attributes = True
