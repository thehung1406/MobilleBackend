from datetime import datetime
from sqlmodel import Session, select
from app.models.booking import Booking
from app.models.booked_room import BookedRoom


class BookingRepository:

    # ---------------- CREATE BOOKING ----------------
    def create_booking(self, session: Session, booking: Booking):
        session.add(booking)
        session.flush()  # booking.id sinh ra
        session.refresh(booking)
        return booking

    # ---------------- CREATE BOOKED ROOMS ----------------
    def add_booked_room(self, session: Session, booked: BookedRoom):
        session.add(booked)
        session.flush()

    # ---------------- CHECK OVERLAPPING ----------------
    def get_overlapping_room(self, session: Session, room_id, checkin, checkout):
        stmt = (
            select(BookedRoom)
            .where(BookedRoom.room_id == room_id)
            .where(BookedRoom.checkin < checkout)
            .where(BookedRoom.checkout > checkin)
        )
        return session.exec(stmt).first()

    # ---------------- EXPIRE PENDING ----------------
    def get_expired_pending_bookings(self, session: Session):
        now = datetime.utcnow()
        stmt = (
            select(Booking)
            .where(Booking.status == "pending")
            .where(Booking.expires_at < now)
        )
        return session.exec(stmt).all()

    # ---------------- UPDATE STATUS (IMPORTANT) ----------------
    def update_booking(self, session: Session, booking: Booking):
        session.add(booking)
        session.commit()
        session.refresh(booking)
        return booking
