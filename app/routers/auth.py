from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from datetime import datetime, timezone, timedelta
import random
from jose import jwt, JWTError

from app.core.database import get_session
from app.core.config import settings
from app.core.redis import add_to_blacklist
from app.schemas.auth import (
    RegisterIn,
    TokenPair,
    RefreshIn,
    RequestVerifyEmailIn,
    VerifyEmailIn,
    RequestPasswordResetIn,
    ConfirmPasswordResetIn,
    LoginOtpVerifyIn,
    LoginResponse,
)
from app.schemas.user import UserOut
from app.models.user import User
from app.models.email_token import EmailToken
from app.utils.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
)
from app.utils.rate_limiter import is_rate_limited
from app.services.task_queue import enqueue_email

router = APIRouter(prefix="/auth", tags=["auth"])


# ============================================================
# 🔐 Đăng ký / Đăng nhập / Refresh / Logout
# ============================================================

@router.post("/register", response_model=UserOut)
def register(payload: RegisterIn, session: Session = Depends(get_session)):
    # check email existed
    if session.exec(select(User).where(User.email == payload.email)).first():
        raise HTTPException(status_code=400, detail="Email exists")

    user = User(
        email=payload.email,
        password_hash=hash_password(payload.password),
        full_name=payload.full_name,
        phone=payload.phone,
        # role mặc định là CUSTOMER trong model -> không đụng
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.post("/login", response_model=LoginResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    """
    Bước 1 của login:

    - Nếu user chưa verify email -> trả token luôn (login bình thường).
    - Nếu user đã verify email    -> gửi OTP qua mail, yêu cầu bước 2.
    """
    user = session.exec(
        select(User).where(User.email == form_data.username)
    ).first()

    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Inactive user")

    # Nếu user CHƯA verify email -> login như cũ
    if not user.email_verified:
        access_token = create_access_token(str(user.id), user.role)
        refresh_token = create_refresh_token(str(user.id))

        return LoginResponse(
            otp_required=False,
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            role=user.role,
            full_name=user.full_name,
            email=user.email,
        )

    # Nếu user ĐÃ verify email -> gửi OTP login
    # Rate limit để tránh spam: 5 lần / 15 phút
    if is_rate_limited(f"login-otp:{user.id}", limit=5, period=15 * 60):
        raise HTTPException(
            status_code=429,
            detail="Too many login OTP requests. Please try again later.",
        )

    # tạo code 6 chữ số, type="login"
    code = "".join(random.choices("0123456789", k=6))
    expires_at = datetime.utcnow() + timedelta(minutes=5)

    # xoá toàn bộ login token cũ (nếu có) cho sạch
    old_tokens = session.exec(
        select(EmailToken).where(
            EmailToken.user_id == user.id,
            EmailToken.type == "login",
        )
    ).all()
    for t in old_tokens:
        session.delete(t)

    login_token = EmailToken(
        user_id=user.id,
        code=code,
        expires_at=expires_at,
        type="login",
    )
    session.add(login_token)
    session.commit()

    # Link FE đẹp cho màn nhập OTP (tuỳ bạn làm route gì)
    login_otp_url = (
        f"{settings.FRONTEND_URL}/login-otp"
        f"?email={user.email}&code={code}"
    )

    html = f"""
    <div style="font-family: Arial, sans-serif; color:#1a202c;">
      <h2 style="color:#2b6cb0; margin-bottom: 8px;">Your login code</h2>
      <p>Hi <strong>{user.full_name or user.email}</strong>,</p>

      <p>Use the code below to complete your login:</p>
      <p style="font-size:28px; letter-spacing:4px; font-weight:bold; margin:12px 0;">
        {code}
      </p>

      <p>Or click the button below to open the login confirmation page:</p>

      <a href="{login_otp_url}"
         style="background:#38a169;color:#ffffff;padding:12px 24px;
                text-decoration:none;border-radius:6px;display:inline-block;
                font-weight:600;margin:16px 0;">
        Confirm Login
      </a>

      <p style="margin-top:8px;">
        This code will expire in <strong>5 minutes</strong>.
      </p>

      <hr style="border:none;border-top:1px solid #e2e8f0;margin:20px 0;" />
      <p style="font-size:12px;color:#718096;">
        If you did not attempt to log in, you can safely ignore this email.
      </p>
    </div>
    """

    enqueue_email(user.email, "Your login code", html)

    # Bước này KHÔNG trả token, chỉ trả cờ otp_required
    return LoginResponse(
        otp_required=True,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
    )


@router.post("/refresh", response_model=TokenPair)
def refresh(payload: RefreshIn, session: Session = Depends(get_session)):
    try:
        data = jwt.decode(
            payload.refresh_token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        if data.get("scope") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid scope")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    uid = data["sub"]
    user = session.exec(select(User).where(User.id == uid)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return TokenPair(
        access_token=create_access_token(str(user.id), user.role),
        refresh_token=create_refresh_token(str(user.id)),
        role=user.role,
        full_name=user.full_name,
        email=user.email,
    )


@router.post("/logout")
def logout(refresh: RefreshIn):
    data = jwt.get_unverified_claims(refresh.refresh_token)
    now_ts = int(datetime.now(tz=timezone.utc).timestamp())
    exp = int(data.get("exp", now_ts))
    ttl = exp - now_ts
    add_to_blacklist(refresh.refresh_token, max(ttl, 60))
    return {"message": "logged out"}


# ============================================================
# 📨 EMAIL VERIFICATION – GỬI CODE + LINK
# ============================================================

@router.post("/request-verify-email")
def request_verify_email(
    payload: RequestVerifyEmailIn,
    session: Session = Depends(get_session),
):
    user = session.exec(select(User).where(User.email == payload.email)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.email_verified:
        raise HTTPException(status_code=400, detail="Email already verified")

    if is_rate_limited(f"verify:{user.id}", limit=3, period=15 * 60):
        raise HTTPException(
            status_code=429,
            detail="Too many verification requests. Please try again later.",
        )

    code = "".join(random.choices("0123456789", k=6))
    expires_at = datetime.utcnow() + timedelta(minutes=5)

    token = EmailToken(
        user_id=user.id,
        code=code,
        expires_at=expires_at,
        type="verify",
    )
    session.add(token)
    session.commit()

    verify_url = (
        f"{settings.FRONTEND_URL}/verify-email"
        f"?email={user.email}&code={code}"
    )

    html = f"""
    <div style="font-family: Arial, sans-serif; color:#1a202c;">
      <h2 style="color:#2b6cb0; margin-bottom: 8px;">Verify your email</h2>
      <p>Hi <strong>{user.full_name or user.email}</strong>,</p>

      <p>Your verification code is:</p>
      <p style="font-size:28px; letter-spacing:4px; font-weight:bold; margin:12px 0;">
        {code}
      </p>

      <p>Or simply click the button below to verify your email:</p>

      <a href="{verify_url}"
         style="background:#38a169;color:#ffffff;padding:12px 24px;
                text-decoration:none;border-radius:6px;display:inline-block;
                font-weight:600;margin:16px 0;">
        Verify Email
      </a>

      <p style="margin-top:16px;">
        This code and link will expire in <strong>5 minutes</strong>.
      </p>

      <hr style="border:none;border-top:1px solid #e2e8f0;margin:20px 0;" />
      <p style="font-size:12px;color:#718096;">
        If you did not request this, you can safely ignore this email.
      </p>
    </div>
    """

    enqueue_email(user.email, "Verify your email", html)
    return {"detail": "Verification code sent"}


@router.post("/verify-email")
def verify_email(
    payload: VerifyEmailIn,
    session: Session = Depends(get_session),
):
    user = session.exec(select(User).where(User.email == payload.email)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    token = session.exec(
        select(EmailToken).where(
            EmailToken.user_id == user.id,
            EmailToken.code == payload.code,
            EmailToken.type == "verify",
        )
    ).first()

    if not token or token.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=400, detail="Invalid or expired verification code"
        )

    user.email_verified = True
    session.add(user)

    tokens = session.exec(
        select(EmailToken).where(
            EmailToken.user_id == user.id,
            EmailToken.type == "verify",
        )
    ).all()
    for t in tokens:
        session.delete(t)

    session.commit()
    return {"detail": "Email verified successfully"}


# ============================================================
# 🔐 PASSWORD RESET – GỬI LINK ĐẶT LẠI MẬT KHẨU
# ============================================================

@router.post("/request-password-reset")
def request_password_reset(
    payload: RequestPasswordResetIn,
    session: Session = Depends(get_session),
):
    user = session.exec(select(User).where(User.email == payload.email)).first()
    if not user:
        return {"detail": "If the email exists, a reset link has been sent"}

    if is_rate_limited(f"pwreset:{user.id}", limit=2, period=24 * 3600):
        raise HTTPException(
            status_code=429,
            detail="Too many password reset requests. Please try again later.",
        )

    token_str = "".join(
        random.choices(
            "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
            k=32,
        )
    )
    expires_at = datetime.utcnow() + timedelta(hours=1)
    reset_token = EmailToken(
        user_id=user.id,
        code=token_str,
        expires_at=expires_at,
        type="reset",
    )
    session.add(reset_token)
    session.commit()

    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token_str}"

    html = f"""
    <div style="font-family: Arial, sans-serif; color:#1a202c;">
      <h2 style="color:#2b6cb0; margin-bottom: 8px;">Password Reset Request</h2>
      <p>Hi <strong>{user.full_name or user.email}</strong>,</p>

      <p>You have requested to reset your password for your Hotel Booking account.</p>
      <p>Click the button below to set a new password:</p>

      <a href="{reset_url}"
         style="background:#3182ce;color:#ffffff;padding:12px 24px;
                text-decoration:none;border-radius:6px;display:inline-block;
                font-weight:600;margin:16px 0;">
        Reset Password
      </a>

      <p style="margin-top:8px;">If the button does not work, copy this link into your browser:</p>
      <p style="word-break:break-all;font-size:13px;color:#2d3748;">{reset_url}</p>

      <p style="margin-top:8px;">
        This link will expire in <strong>1 hour</strong>.
      </p>

      <hr style="border:none;border-top:1px solid #e2e8f0;margin:20px 0;" />
      <p style="font-size:12px;color:#718096;">
        If you did not request a password reset, please ignore this email.
      </p>
    </div>
    """

    enqueue_email(user.email, "Password Reset Request", html)
    return {"detail": "If the email exists, a reset link has been sent"}


@router.post("/confirm-password-reset")
def confirm_password_reset(
    payload: ConfirmPasswordResetIn,
    session: Session = Depends(get_session),
):
    token_entry = session.exec(
        select(EmailToken).where(
            EmailToken.code == payload.token,
            EmailToken.type == "reset",
        )
    ).first()

    if not token_entry or token_entry.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    user = session.get(User, token_entry.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.password_hash = hash_password(payload.new_password)
    session.add(user)
    session.delete(token_entry)
    session.commit()

    return {"detail": "Password reset successfully"}


# ============================================================
# 🆕 BƯỚC 2: XÁC NHẬN LOGIN OTP
# ============================================================

@router.post("/confirm-login-otp", response_model=LoginResponse)
def confirm_login_otp(
    payload: LoginOtpVerifyIn,
    session: Session = Depends(get_session),
):
    """
    Bước 2 của login khi user đã verify email.

    Nhận email + code 6 số -> nếu hợp lệ thì cấp access/refresh token.
    """
    user = session.exec(select(User).where(User.email == payload.email)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not user.email_verified:
        raise HTTPException(
            status_code=400,
            detail="Email is not verified, OTP login is not enabled.",
        )

    token_entry = session.exec(
        select(EmailToken).where(
            EmailToken.user_id == user.id,
            EmailToken.code == payload.code,
            EmailToken.type == "login",
        )
    ).first()

    if not token_entry or token_entry.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Invalid or expired login code")

    # OTP dùng một lần: xoá tất cả token login của user
    tokens = session.exec(
        select(EmailToken).where(
            EmailToken.user_id == user.id,
            EmailToken.type == "login",
        )
    ).all()
    for t in tokens:
        session.delete(t)

    access_token = create_access_token(str(user.id), user.role)
    refresh_token = create_refresh_token(str(user.id))

    session.commit()

    return LoginResponse(
        otp_required=False,
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        role=user.role,
        full_name=user.full_name,
        email=user.email,
    )
