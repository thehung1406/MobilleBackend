from sqlmodel import Session, select
from datetime import datetime, timedelta
from app.models.booking import Booking


class BookingRepository:

    @staticmethod
    def create(session: Session, user_id: int, checkin, checkout, num_guests: int, selected_rooms: list):
        booking = Booking(
            user_id=user_id,
            checkin=checkin,
            checkout=checkout,
            num_guests=num_guests,
            selected_rooms=selected_rooms,
            status="pending",
            expires_at=datetime.utcnow() + timedelta(minutes=2)  # ✅ 2 phút
        )

        session.add(booking)
        session.commit()
        session.refresh(booking)
        return booking

    @staticmethod
    def get_by_user(session: Session, user_id: int):
        stmt = select(Booking).where(Booking.user_id == user_id)
        return session.exec(stmt).all()
