from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List
from datetime import date, datetime, timedelta
from app.core.database import get_session
from app.models.user import User
from app.schemas.user import UserOut, UserCreate, UserUpdate, UserUpdateAdmin
from app.utils.security import hash_password
from app.utils.dependencies import get_current_superuser  # ✅ check quyền admin
from app.models.payment import Payment
from app.models.booking import Booking
from app.models.room import Room
from app.utils.enums import BookingStatus

router = APIRouter(prefix="/admin", tags=["admin"])

# ============================================================
# 👑 Admin User Management (chỉ dành cho Admin)
# ============================================================

@router.get("/users", response_model=List[UserOut])
def list_users(
    session: Session = Depends(get_session),
    current_admin: User = Depends(get_current_superuser),
):
    """📄 Lấy danh sách toàn bộ user (Admin only)."""
    return session.exec(select(User)).all()


@router.get("/users/{user_id}", response_model=UserOut)
def get_user_detail(
    user_id: str,
    session: Session = Depends(get_session),
    current_admin: User = Depends(get_current_superuser),
):
    """🔍 Xem chi tiết thông tin 1 user theo ID."""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/users", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UserCreate,
    session: Session = Depends(get_session),
    current_admin: User = Depends(get_current_superuser),
):
    """➕ Tạo mới user (Admin only)."""
    existing = session.exec(select(User).where(User.email == payload.email)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")

    new_user = User(
        email=payload.email,
        full_name=payload.full_name,
        phone=payload.phone,
        password_hash=hash_password(payload.password),
        role=payload.role,
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user


@router.patch("/users/{user_id}", response_model=UserOut)
def update_user(
    user_id: str,
    payload: UserUpdateAdmin,
    session: Session = Depends(get_session),
    current_admin: User = Depends(get_current_superuser),
):
    """✏️ Cập nhật thông tin user (Admin only)."""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # ✅ Nếu admin gửi password mới -> hash lại
    data = payload.dict(exclude_unset=True)
    if "password" in data:
        user.password_hash = hash_password(data.pop("password"))

    # ✅ Cập nhật các field còn lại
    for field, value in data.items():
        setattr(user, field, value)

    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: str,
    session: Session = Depends(get_session),
    current_admin: User = Depends(get_current_superuser),
):
    """🗑️ Xóa user (Admin only)."""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    session.delete(user)
    session.commit()
    return {"detail": "User deleted successfully"}


# ============================================================
# 📊 Admin Analytics
# ============================================================

@router.get("/analytics/overview")
def analytics_overview(
    session: Session = Depends(get_session),
    current_admin: User = Depends(get_current_superuser),
):
    """
    Return an overview of key business metrics:
    - total_revenue_today: sum of payments made today.
    - cancellation_rate: percentage of bookings that have been cancelled.
    """
    today = date.today()
    # Payments created between start of today and start of tomorrow
    start = datetime.combine(today, datetime.min.time())
    end = start + timedelta(days=1)
    payments_today = session.exec(
        select(Payment).where(Payment.created_at >= start, Payment.created_at < end)
    ).all()
    total_revenue_today = sum(p.amount for p in payments_today)

    bookings = session.exec(select(Booking)).all()
    total_bookings = len(bookings)
    cancelled_count = sum(1 for b in bookings if b.status == BookingStatus.CANCELLED)
    cancellation_rate = (cancelled_count / total_bookings) if total_bookings else 0.0

    return {
        "total_revenue_today": total_revenue_today,
        "cancellation_rate": cancellation_rate,
    }


@router.get("/analytics/revenue")
def analytics_revenue(
    from_date: date,
    to_date: date,
    session: Session = Depends(get_session),
    current_admin: User = Depends(get_current_superuser),
):
    """
    Return revenue aggregated between two dates and broken down by day.

    Query parameters:
    - from_date: start date (inclusive)
    - to_date: end date (inclusive)
    """
    if from_date > to_date:
        raise HTTPException(status_code=400, detail="from_date must be before to_date")

    start = datetime.combine(from_date, datetime.min.time())
    end = datetime.combine(to_date + timedelta(days=1), datetime.min.time())
    payments = session.exec(
        select(Payment).where(Payment.created_at >= start, Payment.created_at < end)
    ).all()

    total_revenue = sum(p.amount for p in payments)
    revenue_by_day: dict[date, float] = {}
    for p in payments:
        d = p.created_at.date()
        revenue_by_day[d] = revenue_by_day.get(d, 0.0) + p.amount

    # Convert keys to ISO format strings for JSON serialization
    revenue_by_day_str = {d.isoformat(): amt for d, amt in revenue_by_day.items()}

    return {
        "total_revenue": total_revenue,
        "revenue_by_day": revenue_by_day_str,
    }
