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

    # ========================================================
    # VALIDATION: DATE
    # ========================================================
    def validate_dates(self, checkin: str, checkout: str):
        try:
            checkin_dt = datetime.strptime(checkin, "%Y-%m-%d").date()
            checkout_dt = datetime.strptime(checkout, "%Y-%m-%d").date()
        except Exception:
            raise ValueError("Invalid date format. Use YYYY-MM-DD")

        if checkin_dt >= checkout_dt:
            raise ValueError("Checkout date must be after checkin")

        return checkin_dt, checkout_dt

    # ========================================================
    # VALIDATION: CAPACITY
    # ========================================================
    def validate_capacity(self, rooms: List[Room], num_guests: int):
        total_capacity = sum(r.room_type.max_occupancy for r in rooms)
        if num_guests > total_capacity:
            raise ValueError("Number of guests exceeds room capacity")

    # ========================================================
    # CHECK ROOM AVAILABILITY
    # ========================================================
    def is_room_available(self, session: Session, room_id: int, checkin, checkout):
        """Kiểm tra phòng có trống không"""
        return self.repo.get_overlapping_room(session, room_id, checkin, checkout) is None

    # ========================================================
    # CREATE BOOKING
    # ========================================================
    def process_booking(self, data: dict) -> Booking:
        """
        Main logic tạo booking:
        - Validate user
        - Validate phòng
        - Validate ngày
        - Check phòng có bị booked overlap không
        - Tạo booking + booked room
        """

        user_id = data["user_id"]
        room_ids: List[int] = data["room_ids"]
        num_guests = data["num_guests"]
        checkin = data["checkin"]
        checkout = data["checkout"]
        price = data["price"]

        # --- Validate dates ---
        checkin_dt, checkout_dt = self.validate_dates(checkin, checkout)

        with Session(engine) as session:

            # ---------------------------
            # 1. Validate user
            # ---------------------------
            user = session.get(User, user_id)
            if not user:
                raise ValueError("User not found")

            # ---------------------------
            # 2. Load rooms
            # ---------------------------
            rooms = session.exec(select(Room).where(Room.id.in_(room_ids))).all()

            if not rooms or len(rooms) != len(room_ids):
                raise ValueError("Some rooms not found")

            # ---------------------------
            # 3. Validate room status
            # ---------------------------
            for room in rooms:
                if not room.is_active:
                    raise ValueError(f"Room {room.id} is inactive")
                if not room.room_type.is_active:
                    raise ValueError(f"Room type {room.room_type.id} is inactive")
                if not room.room_type.property.is_active:
                    raise ValueError("Property is inactive")

            # ---------------------------
            # 4. Validate capacity
            # ---------------------------
            self.validate_capacity(rooms, num_guests)

            # ---------------------------
            # 5. Check room availability
            # ---------------------------
            for room_id in room_ids:
                if not self.is_room_available(session, room_id, checkin_dt, checkout_dt):
                    raise ValueError(f"Room {room_id} is already booked in this period")

            # ---------------------------
            # 6. Create booking
            # ---------------------------
            booking = Booking(
                user_id=user_id,
                booking_date=datetime.utcnow().date(),
                status="pending",
                expires_at=datetime.utcnow() + timedelta(minutes=15)
            )

            booking = self.repo.create_booking(session, booking)

            # ---------------------------
            # 7. Create booked rooms
            # ---------------------------
            for room_id in room_ids:
                booked = BookedRoom(
                    room_id=room_id,
                    booking_id=booking.id,
                    checkin=checkin_dt,
                    checkout=checkout_dt,
                    price=price,
                )
                self.repo.add_booked_room(session, booked)

            session.commit()
            logger.info(f"[Booking] Created pending booking #{booking.id}")

            return booking

    # ========================================================
    # EXPIRE PENDING BOOKINGS
    # ========================================================
    def expire_pending_bookings(self, session: Session):
        """Worker chạy định kỳ để hủy booking pending"""
        expired = self.repo.get_expired_pending_bookings(session)

        for booking in expired:
            booking.status = "expired"

        session.commit()

        if expired:
            logger.info(f"[Booking] Expired {len(expired)} pending bookings")
