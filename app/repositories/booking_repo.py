from datetime import datetime
from sqlmodel import Session, select
from app.models.booking import Booking
from app.models.booked_room import BookedRoom


class BookingRepository:

    # ---------------- CREATE BOOKING ----------------
    def create_booking(self, session: Session, booking: Booking):
        session.add(booking)
        session.flush()       # booking.id available
        session.refresh(booking)
        return booking

    # ---------------- CREATE BOOKED ROOMS ----------------
    def add_booked_room(self, session: Session, booked: BookedRoom):
        session.add(booked)
        session.flush()
        return booked

    # ---------------- CHECK OVERLAPPING ----------------
    def get_overlapping_room(self, session: Session, room_id, checkin, checkout):
        stmt = (
            select(BookedRoom)
            .where(BookedRoom.room_id == room_id)
            .where(BookedRoom.checkin < checkout)
            .where(BookedRoom.checkout > checkin)
        )
        return session.exec(stmt).first()

    # ---------------- LIST BOOKED ROOMS BY BOOKING ----------------
    def list_booked_rooms(self, session: Session, booking_id: int):
        stmt = select(BookedRoom).where(BookedRoom.booking_id == booking_id)
        return session.exec(stmt).all()

    # ---------------- GET BOOKING BY ID ----------------
    def get_booking(self, session: Session, booking_id: int):
        return session.get(Booking, booking_id)

    # ---------------- LIST BOOKINGS BY USER ----------------
    def list_bookings_by_user(self, session: Session, user_id: int):
        stmt = (
            select(Booking)
            .where(Booking.user_id == user_id)
            .order_by(Booking.booking_date.desc())
        )
        return session.exec(stmt).all()

    # ---------------- EXPIRE PENDING BOOKINGS ----------------
    def get_expired_pending_bookings(self, session: Session):
        now = datetime.utcnow()
        stmt = (
            select(Booking)
            .where(Booking.status == "pending")
            .where(Booking.expires_at < now)
        )
        return session.exec(stmt).all()

    # ---------------- UPDATE STATUS / BOOKING ----------------
    def update_booking(self, session: Session, booking: Booking):
        session.add(booking)
        session.commit()
        session.refresh(booking)
        return booking
