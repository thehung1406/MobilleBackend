from pydantic import BaseModel
from typing import List, Optional
from app.schemas.review import ReviewRead


class RoomRead(BaseModel):
    id: int
    name: str
    image: Optional[str]
    is_active: bool
    room_type_id: int

    class Config:
        from_attributes = True


class RoomTypeWithRoomsRead(BaseModel):
    id: int
    name: str
    price: int
    max_occupancy: int
    is_active: bool
    rooms: List[RoomRead]

    class Config:
        from_attributes = True


class PropertyDetailRead(BaseModel):
    id: int
    name: str
    description: Optional[str]
    address: Optional[str]
    image: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    checkin: Optional[str]
    checkout: Optional[str]
    contact: Optional[str]

    room_types: List[RoomTypeWithRoomsRead]
    reviews: List[ReviewRead] = []   # 🔥 ADD THIS

    class Config:
        from_attributes = True
