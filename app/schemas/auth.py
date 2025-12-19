from pydantic import BaseModel, EmailStr
from typing import Optional
from app.utils.enums import UserRole



class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenData(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"



class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    phone: Optional[str] = None



class StaffCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    phone: Optional[str] = None
    property_id: int


class UserUpdate(BaseModel):
    full_name: Optional[str]
    phone: Optional[str]


class UserRead(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    phone: Optional[str]
    role: UserRole

    class Config:
        from_attributes = True

