from pydantic import BaseModel
from typing import Optional



class PropertyBase(BaseModel):
    name: str
    description: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    image: Optional[str] = None
    checkin: Optional[str] = None
    checkout: Optional[str] = None
    contact: Optional[str] = None
    is_active: Optional[bool] = None




class PropertyCreate(PropertyBase):
    pass



class PropertyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    image: Optional[str] = None
    checkin: Optional[str] = None
    checkout: Optional[str] = None
    contact: Optional[str] = None



class PropertyRead(PropertyBase):
    id: int

    class Config:
        from_attributes = True
