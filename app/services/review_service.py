# app/services/review_service.py

from sqlmodel import Session, select
from fastapi import HTTPException, status

from app.repositories.review_repo import ReviewRepository
from app.models.booking import Booking
from app.models.booked_room import BookedRoom
from app.models.room import Room
from app.models.room_type import RoomType
from app.schemas.review import ReviewCreate, ReviewUpdate
from app.utils.enums import UserRole


class ReviewService:

    def __init__(self):
        self.repo = ReviewRepository()

    # ===========================================================
    # 🔹 CREATE REVIEW — CUSTOMER ONLY
    # ===========================================================
    def create(self, session: Session, user, data: ReviewCreate):

        # Tìm booking đã trả tiền của user tại property
        paid_booking = session.exec(
            select(Booking)
            .where(Booking.user_id == user.id)
            .where(Booking.status == "paid")
        ).all()

        if not paid_booking:
            raise HTTPException(403, "Bạn chưa có booking đã thanh toán!")

        # Kiểm tra booked_rooms xem có thuộc property muốn review không
        valid_booking = False

        for booking in paid_booking:
            booked_rooms = session.exec(
                select(BookedRoom).where(BookedRoom.booking_id == booking.id)
            ).all()

            for br in booked_rooms:
                room = session.get(Room, br.room_id)
                room_type = session.get(RoomType, room.room_type_id)

                if room_type.property_id == data.property_id:
                    valid_booking = True
                    break

            if valid_booking:
                break

        if not valid_booking:
            raise HTTPException(
                status_code=403,
                detail="Bạn phải có booking đã thanh toán tại khách sạn này mới được đánh giá."
            )

        payload = data.model_dump()
        payload["user_id"] = user.id

        return self.repo.create(session, payload)

    # ===========================================================
    # 🔹 LIST REVIEW THEO PROPERTY
    # ===========================================================
    def list_by_property(self, session: Session, property_id: int):
        return self.repo.list_by_property(session, property_id)

    # ===========================================================
    # 🔹 UPDATE REVIEW — Customer Only
    # ===========================================================
    def update(self, session: Session, review_id: int, user, data: ReviewUpdate):
        review = self.repo.get(session, review_id)

        if not review:
            raise HTTPException(404, "Review không tồn tại")

        if review.user_id != user.id:
            raise HTTPException(403, "Bạn chỉ được sửa review của chính bạn")

        return self.repo.update(
            session,
            review_id,
            data.model_dump(exclude_unset=True)
        )

    # ===========================================================
    # 🔹 DELETE REVIEW — Phân quyền chuẩn
    # ===========================================================
    def delete(self, session: Session, review_id: int, user):
        review = self.repo.get(session, review_id)
        if not review:
            raise HTTPException(404, "Review không tồn tại")

        # CUSTOMER → Chỉ được xoá review của chính họ
        if user.role == UserRole.CUSTOMER and user.id != review.user_id:
            raise HTTPException(403, "Bạn không thể xoá review của người khác")

        # STAFF → Chỉ được xoá review của property họ quản lý
        if user.role == UserRole.STAFF and user.property_id != review.property_id:
            raise HTTPException(403, "Bạn không có quyền xoá review này")

        # SUPER ADMIN → xoá bất kỳ
        self.repo.delete(session, review_id)
        return True
