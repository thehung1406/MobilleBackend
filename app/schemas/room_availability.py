from pydantic import BaseModel
from datetime import date

class RoomAvailabilityRequest(BaseModel):
    checkin: date
    checkout: date

class RoomAvailabilityResponse(BaseModel):
    room_id: int
    available: bool
