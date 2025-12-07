from pydantic import BaseModel, EmailStr
from typing import Optional
from app.utils.enums import UserRole


class RegisterIn(BaseModel):
    email: str
    password: str
    full_name: str
    phone: str


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    role: str          # ✅ thêm role
    full_name: str     # ✅ tùy bạn muốn FE hiển thị
    email: str


class RefreshIn(BaseModel):
    refresh_token: str

# New schemas for email verification and password reset flows

class RequestVerifyEmailIn(BaseModel):
    """Request to send a verification code to the user's email."""
    email: str


class VerifyEmailIn(BaseModel):
    """Payload to verify an email with a code."""
    email: str
    code: str


class RequestPasswordResetIn(BaseModel):
    """Request to initiate a password reset email."""
    email: str


class ConfirmPasswordResetIn(BaseModel):
    """Confirm password reset using a token."""
    token: str
    new_password: str

class LoginOtpVerifyIn(BaseModel):
    """
    Body cho bước xác thực OTP khi login.
    FE sẽ gửi email + code (6 số) mà user nhận được.
    """
    email: str
    code: str


class LoginResponse(BaseModel):
    """
    Response thống nhất cho /auth/login và /auth/confirm-login-otp.

    - Nếu otp_required = False  -> có đủ access_token / refresh_token
    - Nếu otp_required = True   -> chỉ trả email + cờ otp_required,
      FE phải gọi /auth/confirm-login-otp để lấy token.
    """
    otp_required: bool = False

    # Các field dưới đây chỉ có khi đã hoàn thành login (không cần OTP nữa)
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_type: Optional[str] = "bearer"
    role: Optional[UserRole| str] = None
    full_name: Optional[str] = None
    email: Optional[str] = None
