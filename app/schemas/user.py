from pydantic import BaseModel, EmailStr
from typing import Optional
from app.utils.enums import UserRole


# ======================
# BASE
# ======================
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    phone: Optional[str] = None


# ======================
# CREATE NORMAL USER
# ======================
class UserCreate(UserBase):
    password: str
    role: UserRole = UserRole.CUSTOMER
    property_id: Optional[int] = None   # chỉ staff mới dùng


# ======================
# UPDATE
# ======================
class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None


# ======================
# READ RESPONSE
# ======================
class UserRead(UserBase):
    id: int
    role: UserRole
    property_id: Optional[int]

    class Config:
        from_attributes = True


# ======================
# STAFF CREATE
# ======================
class StaffCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    phone: Optional[str] = None
    property_id: int


class StaffRead(UserRead):
    pass
