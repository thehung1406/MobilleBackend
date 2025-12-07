# app/services/review_service.py
from sqlmodel import Session, select
from fastapi import HTTPException

from app.repositories.review_repo import ReviewRepository
from app.models.booking import Booking
from app.schemas.review import ReviewCreate, ReviewUpdate


class ReviewService:

    def __init__(self):
        self.repo = ReviewRepository()

    # -------------------------------------------------
    # CREATE REVIEW — CUSTOMER ONLY
    # -------------------------------------------------
    def create(self, session: Session, user, data: ReviewCreate):
        # Customer phải có booking đã PAID thuộc property đó
        paid_booking = session.exec(
            select(Booking).where(
                Booking.user_id == user.id,
                Booking.property_id == data.property_id,
                Booking.status == "paid"
            )
        ).first()

        if not paid_booking:
            raise HTTPException(
                status_code=403,
                detail="Bạn phải có booking đã thanh toán ở khách sạn này mới được đánh giá."
            )

        payload = data.model_dump()
        payload["user_id"] = user.id

        return self.repo.create(session, payload)

    # -------------------------------------------------
    # LIST REVIEW THEO PROPERTY
    # -------------------------------------------------
    def list_by_property(self, session: Session, property_id: int):
        return self.repo.list_by_property(session, property_id)

    # -------------------------------------------------
    # CUSTOMER UPDATE REVIEW CỦA CHÍNH MÌNH
    # -------------------------------------------------
    def update(self, session: Session, review_id: int, user, data: ReviewUpdate):
        review = self.repo.get(session, review_id)
        if not review:
            raise HTTPException(404, "Review không tồn tại")

        if review.user_id != user.id:
            raise HTTPException(403, "Bạn chỉ được sửa review của chính mình")

        return self.repo.update(session, review_id, data.model_dump(exclude_unset=True))

    # -------------------------------------------------
    # DELETE REVIEW
    # customer → xoá review của mình
    # staff → xoá review thuộc property họ quản lý
    # super_admin → xoá mọi review
    # -------------------------------------------------
    def delete(self, session: Session, review_id: int, user):
        review = self.repo.get(session, review_id)
        if not review:
            raise HTTPException(404, "Review không tồn tại")

        # Customer → chỉ được xoá review của họ
        if user.role == "customer" and user.id != review.user_id:
            raise HTTPException(403, "Bạn không thể xoá review của người khác")

        # Staff → chỉ xoá review thuộc property họ quản lý
        if user.role == "staff" and user.property_id != review.property_id:
            raise HTTPException(403, "Không có quyền xoá review này")

        # Super Admin → được xoá hết
        self.repo.delete(session, review_id)
        return True
