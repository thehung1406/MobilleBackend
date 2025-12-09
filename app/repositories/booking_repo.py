from sqlmodel import Session
from app.models.booking import Booking
from datetime import datetime, timedelta

class BookingRepository:

    @staticmethod
    def create(session: Session, user_id: int, checkin, checkout, num_guests: int):
        booking = Booking(
            user_id=user_id,
            checkin=checkin,
            checkout=checkout,
            num_guests=num_guests,
            status="pending",
            expires_at=datetime.utcnow() + timedelta(minutes=15)
        )
        session.add(booking)
        session.commit()
        session.refresh(booking)
        return booking
