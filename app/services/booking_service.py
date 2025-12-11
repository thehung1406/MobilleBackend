from sqlmodel import Session, select
from datetime import datetime

from app.models import Booking, BookedRoom
from app.repositories.booking_repo import BookingRepository
from app.repositories.booked_room_repo import BookedRoomRepository
from app.repositories.room_repo import RoomRepository
from app.models.room import Room
from app.utils.lock import acquire_room_lock, release_room_lock


class BookingService:

    @staticmethod
    def create_booking(session: Session, user_id: int, payload):

        checkin = payload.checkin
        checkout = payload.checkout
        selected_rooms = payload.room_ids

        if not selected_rooms:
            raise Exception("Vui lòng chọn ít nhất 1 phòng")

        # CHECK & LOCK THEO NGÀY
        for room_id in selected_rooms:

            if not RoomRepository.is_available(session, room_id, checkin, checkout):
                raise Exception(f"Phòng {room_id} không còn trống")

            ok = acquire_room_lock(room_id, checkin, checkout)
            if not ok:
                raise Exception(f"Phòng {room_id} đang được người khác giữ")

        # Tạo booking pending
        booking = BookingRepository.create(
            session=session,
            user_id=user_id,
            checkin=checkin,
            checkout=checkout,
            num_guests=payload.num_guests,
            selected_rooms=selected_rooms
        )

        # Tính tiền
        nights = (checkout - checkin).days
        total = 0
        for rid in selected_rooms:
            room = session.get(Room, rid)
            total += room.room_type.price * nights

        return {
            "booking_id": booking.id,
            "rooms": selected_rooms,
            "amount": total,
            "expires_at": booking.expires_at,
            "status": "pending"
        }


    @staticmethod
    def get_my_bookings(session: Session, user_id: int):
        return BookingRepository.get_by_user(session, user_id)


    @staticmethod
    def cancel_booking(session: Session, booking_id: int, user_id: int):

        booking = session.get(Booking, booking_id)
        if not booking:
            raise Exception("Booking không tồn tại")

        if booking.user_id != user_id:
            raise Exception("Không có quyền hủy booking này")

        # Nếu booking pending → release lock đúng ngày
        if booking.status == "pending":
            for rid in booking.selected_rooms:
                release_room_lock(rid, booking.checkin, booking.checkout)

            booking.status = "cancelled"
            session.commit()
            return {"status": "cancelled"}

        # Nếu booking confirmed → xóa booked room
        if booking.status == "confirmed":
            rows = session.exec(
                select(BookedRoom).where(BookedRoom.booking_id == booking.id)
            ).all()

            for row in rows:
                session.delete(row)

            booking.status = "cancelled"
            session.commit()
            return {"status": "cancelled"}

        return {"status": booking.status}
