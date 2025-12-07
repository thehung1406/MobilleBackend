from pydantic import BaseModel
from typing import Optional


class RoomTypeCreate(BaseModel):
    property_id: int
    price: int
    name: str
    max_occupancy: int
    is_active: bool = True


class RoomTypeUpdate(BaseModel):
    price: Optional[int] = None
    name: Optional[str] = None
    max_occupancy: Optional[int] = None
    is_active: Optional[bool] = None


class RoomTypeRead(BaseModel):
    id: int
    property_id: int
    price: int
    name: str
    max_occupancy: int
    is_active: bool

    class Config:
        from_attributes = True
