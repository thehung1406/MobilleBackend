from pydantic import BaseModel
from typing import List, Optional
from datetime import date


class SearchRequest(BaseModel):
    property_id: int
    checkin: date
    checkout: date
    num_guests: int
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    amenities: Optional[List[int]] = None  # list amenity_id


class AvailableRoom(BaseModel):
    room_id: int
    room_number: str


class AvailableRoomType(BaseModel):
    id: int
    name: str
    price: float
    max_occupancy: int
    room_count: int
    available_rooms: List[AvailableRoom]


class SearchResponse(BaseModel):
    property_id: int
    checkin: date
    checkout: date
    room_types: List[AvailableRoomType]
