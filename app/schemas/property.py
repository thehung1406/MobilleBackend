from pydantic import BaseModel
from typing import Optional


# ======================
# BASE
# ======================
class PropertyBase(BaseModel):
    name: str
    description: Optional[str] = None
    address: Optional[str] = None
    province: Optional[str] = None        # ⭐ MUST HAVE ⭐
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    image: Optional[str] = None
    checkin: Optional[str] = None
    checkout: Optional[str] = None
    contact: Optional[str] = None
    cancel_policy: Optional[str] = None


# ======================
# CREATE
# ======================
class PropertyCreate(PropertyBase):
    pass


# ======================
# UPDATE
# ======================
class PropertyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None
    province: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    image: Optional[str] = None
    checkin: Optional[str] = None
    checkout: Optional[str] = None
    contact: Optional[str] = None
    cancel_policy: Optional[str] = None


# ======================
# READ
# ======================
class PropertyRead(PropertyBase):
    id: int

    class Config:
        from_attributes = True
