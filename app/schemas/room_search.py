from pydantic import BaseModel
from typing import List, Optional
from datetime import date


class RoomSearchRequest(BaseModel):
    property_id: int
    checkin: date
    checkout: date
    num_guests: int
    min_price: Optional[int] = None
    max_price: Optional[int] = None
    amenities: Optional[List[int]] = None


class AvailableRoom(BaseModel):
    room_id: int
    room_number: str


class AvailableRoomType(BaseModel):
    id: int
    name: str
    price: int
    max_occupancy: int
    room_count: int
    available_rooms: List[AvailableRoom]


class RoomSearchResponse(BaseModel):
    property_id: int
    checkin: date
    checkout: date
    room_types: List[AvailableRoomType]
