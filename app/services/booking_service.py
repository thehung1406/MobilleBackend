from sqlmodel import Session,select
from app.repositories.booking_repo import BookingRepository
from app.repositories.booked_room_repo import BookedRoomRepository
from app.repositories.room_repo import RoomRepository
from app.utils.lock import acquire_room_lock, release_room_lock
from app.models.room_type import RoomType
from app.models.room import Room


class BookingService:

    @staticmethod
    def create_booking(session: Session, user_id: int, payload):
        checkin = payload.checkin
        checkout = payload.checkout

        selected_rooms = []  # list các room_id đã chọn để lưu booked_room
        locks = []  # danh sách lock đã acquire để rollback nếu lỗi

        # -----------------------------------------------
        # 1. Lặp qua từng room_type FE yêu cầu
        # -----------------------------------------------
        for req in payload.rooms:
            room_type = session.get(RoomType, req.room_type_id)
            if not room_type:
                raise Exception("RoomType không tồn tại")

            # lấy toàn bộ phòng của room_type này
            rooms = session.exec(
                select(Room).where(Room.room_type_id == room_type.id)
            ).all()

            # tìm phòng trống
            available_rooms = []
            for room in rooms:
                if RoomRepository.is_available(session, room.id, checkin, checkout):
                    available_rooms.append(room.id)

            if len(available_rooms) < req.quantity:
                raise Exception("Không đủ phòng trống")

            # lock từng phòng
            for i in range(req.quantity):
                room_id = available_rooms[i]
                ok = acquire_room_lock(room_id)
                if not ok:
                    raise Exception("Phòng đang được đặt bởi khách khác")
                locks.append(room_id)
                selected_rooms.append(room_id)

        # -----------------------------------------------
        # 2. Tạo booking record
        # -----------------------------------------------
        booking = BookingRepository.create(
            session, user_id, checkin, checkout, payload.num_guests
        )

        # -----------------------------------------------
        # 3. Tạo booked_room record
        # -----------------------------------------------
        for room_id in selected_rooms:
            BookedRoomRepository.create(
                session, booking.id, room_id, checkin, checkout
            )

        # -----------------------------------------------
        # 4. Tính tổng tiền
        # -----------------------------------------------
        nights = (checkout - checkin).days
        total_amount = 0
        for req in payload.rooms:
            rt = session.get(RoomType, req.room_type_id)
            total_amount += rt.price * nights * req.quantity

        # -----------------------------------------------
        # 5. Trả kết quả FE → bước tiếp theo là payment
        # -----------------------------------------------
        return {
            "booking_id": booking.id,
            "amount": total_amount,
            "expires_at": booking.expires_at,
            "status": "pending"
        }
