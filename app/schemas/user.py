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
# CREATE CUSTOMER
# ======================
class UserCreate(UserBase):
    password: str


# ======================
# STAFF CREATE (SUPER ADMIN)
# ======================
class StaffCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    phone: Optional[str] = None
    property_id: int   # staff MUST have property


# ======================
# UPDATE PROFILE
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
    property_id: Optional[int] = None

    class Config:
        from_attributes = True
