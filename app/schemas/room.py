from pydantic import BaseModel
from typing import Optional


class RoomBase(BaseModel):
    name: str
    image: Optional[str] = None
    is_active: bool = True


class RoomCreate(RoomBase):
    room_type_id: int


class RoomUpdate(BaseModel):
    name: Optional[str] = None
    image: Optional[str] = None
    is_active: Optional[bool] = None


class RoomRead(RoomBase):
    id: int
    room_type_id: int

    class Config:
        from_attributes = True
