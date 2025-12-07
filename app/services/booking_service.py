from datetime import datetime, timedelta
from typing import List
from sqlmodel import Session, select

from app.core.logger import logger
from app.core.database import engine
from app.models.booking import Booking
from app.models.booked_room import BookedRoom
from app.models.room import Room
from app.models.user import User
from app.repositories.booking_repo import BookingRepository


class BookingService:

    def __init__(self):
        self.repo = BookingRepository()

    # ---------------- VALIDATION ----------------

    def validate_dates(self, checkin: str, checkout: str):
        checkin_dt = datetime.strptime(checkin, "%Y-%m-%d")
        checkout_dt = datetime.strptime(checkout, "%Y-%m-%d")

        if checkin_dt >= checkout_dt:
            raise ValueError("Checkout must be after checkin")

        return checkin_dt, checkout_dt

    def validate_capacity(self, rooms: List[Room], num_guests: int):
        total_capacity = sum(room.room_type.max_occupancy for room in rooms)
        if num_guests > total_capacity:
            raise ValueError("Số lượng khách vượt quá sức chứa phòng")

    # ---------------- CHECK ROOM ----------------

    def is_room_available(self, session: Session, room_id, checkin, checkout):
        return (
            self.repo.get_overlapping_room(session, room_id, checkin, checkout)
            is None
        )

    # ---------------- CREATE BOOKING ----------------

    def process_booking(self, data: dict) -> Booking:

        user_id = data["user_id"]
        room_ids: List[int] = data["room_ids"]
        num_guests = data["num_guests"]
        checkin = data["checkin"]
        checkout = data["checkout"]
        price = data["price"]

        checkin_dt, checkout_dt = self.validate_dates(checkin, checkout)

        with Session(engine) as session:
            user = session.get(User, user_id)
            if not user:
                raise ValueError("User not found")

            # Load rooms
            rooms = session.exec(select(Room).where(Room.id.in_(room_ids))).all()

            if not rooms:
                raise ValueError("Rooms not found")

            # Validate status
            for room in rooms:
                if not room.is_active:
                    raise ValueError(f"Room {room.id} is inactive")
                if not room.room_type.is_active:
                    raise ValueError(f"Room type inactive")
                if not room.room_type.property.is_active:
                    raise ValueError(f"Property inactive")

            # Validate capacity
            self.validate_capacity(rooms, num_guests)

            # Check availability
            for room_id in room_ids:
                if not self.is_room_available(session, room_id, checkin, checkout):
                    raise ValueError(f"Room {room_id} already booked")

            # Create booking
            booking = Booking(
                user_id=user_id,
                booking_date=datetime.utcnow().date(),
                status="pending",
                expires_at=datetime.utcnow() + timedelta(minutes=15)
            )

            booking = self.repo.create_booking(session, booking)

            # Create booked rooms
            for room_id in room_ids:
                booked = BookedRoom(
                    room_id=room_id,
                    booking_id=booking.id,
                    checkin=checkin,
                    checkout=checkout,
                    price=price,
                )
                self.repo.add_booked_room(session, booked)

            logger.info(f"[Booking] Created pending booking #{booking.id}")
            return booking

    # ---------------- EXPIRE PENDING ----------------

    def expire_pending_bookings(self, session: Session):
        expired = self.repo.get_expired_pending_bookings(session)

        for booking in expired:
            booking.status = "expired"

        session.commit()
