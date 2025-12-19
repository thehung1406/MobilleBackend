from pydantic import BaseModel, EmailStr
from typing import Optional
from app.utils.enums import UserRole



class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    phone: Optional[str] = None



class UserCreate(UserBase):
    password: str



class StaffCreate(UserBase):
    password: str
    property_id: int



class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None


class UserRead(UserBase):
    id: int
    role: UserRole
    property_id: Optional[int] = None

    class Config:
        from_attributes = True
