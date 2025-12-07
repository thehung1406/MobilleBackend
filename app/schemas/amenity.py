from pydantic import BaseModel
from typing import Optional


class AmenityBase(BaseModel):
    name: str
    icon: Optional[str] = None
    description: Optional[str] = None


class AmenityCreate(AmenityBase):
    pass


class AmenityUpdate(BaseModel):
    name: Optional[str] = None
    icon: Optional[str] = None
    description: Optional[str] = None


class AmenityRead(AmenityBase):
    id: int

    class Config:
        from_attributes = True
