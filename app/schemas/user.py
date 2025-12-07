from typing import Optional
from pydantic import BaseModel
from datetime import datetime
import uuid
from app.utils.enums import UserRole


# ============================================================
# 📤 OUTPUT SCHEMA
# ============================================================
class UserOut(BaseModel):
    id: uuid.UUID
    email: str
    full_name: str
    phone: str
    role: UserRole        # 🔁 dùng Enum luôn, API trả về vẫn là "ADMIN" / "CUSTOMER"
    is_active: bool
    email_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True   # chuẩn cho Pydantic v2


# ============================================================
# ✏️ UPDATE SCHEMA
# ============================================================
class UserUpdate(BaseModel):
    email: Optional[str] = None
    password: Optional[str] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None

class UserUpdateAdmin(BaseModel):
    email: Optional[str] = None
    password: Optional[str] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[UserRole] = None     # ⭐ Admin được phép cập nhật role
    is_active: Optional[bool] = None    # ⭐ Admin được phép bật/tắt tài khoản


# ============================================================
# 🧩 CREATE SCHEMA
# ============================================================
class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str
    phone: str
    # 👉 Dùng Enum, Pydantic tự convert từ string "ADMIN" / "CUSTOMER"
    role: UserRole = UserRole.CUSTOMER
    is_active: bool = True
