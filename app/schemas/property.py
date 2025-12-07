from pydantic import BaseModel
from typing import Optional


class PropertyCreate(BaseModel):
    name: str
    description: Optional[str] = None
    address: Optional[str] = None
    is_active: bool = True
    checkin: Optional[str] = None
    checkout: Optional[str] = None
    contact: Optional[str] = None
    image: Optional[str] = None
    cancel_policy: Optional[str] = None


class PropertyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None
    is_active: Optional[bool] = None
    checkin: Optional[str] = None
    checkout: Optional[str] = None
    contact: Optional[str] = None
    image: Optional[str] = None
    cancel_policy: Optional[str] = None


class PropertyRead(BaseModel):
    id: int
    name: str
    description: Optional[str]
    address: Optional[str]
    is_active: bool
    checkin: Optional[str]
    checkout: Optional[str]
    contact: Optional[str]
    image: Optional[str]
    cancel_policy: Optional[str]

    class Config:
        from_attributes = True
