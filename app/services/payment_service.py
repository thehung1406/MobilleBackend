import uuid
from datetime import datetime
from sqlmodel import Session

from app.models import Payment
from app.repositories.booked_room_repo import BookedRoomRepository
from app.repositories.payment_repo import PaymentRepository
from app.models.booking import Booking
from app.utils.lock import release_room_lock
from app.utils.qr_generator import generate_qr_base64


class PaymentService:

    @staticmethod
    def create_payment(session: Session, booking_id: int, amount: float, payment_type: str):

        booking = session.get(Booking, booking_id)
        if not booking:
            raise Exception("Booking không tồn tại")

        payment = PaymentRepository.create(
            session=session,
            booking_id=booking_id,
            amount=amount,
            payment_type=payment_type
        )

        payment_code = f"PAY-{uuid.uuid4().hex[:8].upper()}"
        qr_data = f"Thanh toán booking #{booking_id} | Code: {payment_code}"
        qr_base64 = generate_qr_base64(qr_data)

        return {
            "payment_id": payment.id,
            "booking_id": booking_id,
            "amount": amount,
            "payment_code": payment_code,
            "qr_base64": qr_base64,
            "status": "pending"
        }


    @staticmethod
    def confirm_payment(session: Session, payment_id: int):

        payment = session.get(Payment, payment_id)
        if not payment:
            raise Exception("Payment không tồn tại")

        booking = payment.booking
        if not booking:
            raise Exception("Booking không tồn tại")

        # Booking expired
        if booking.expires_at < datetime.utcnow():

            for rid in booking.selected_rooms:
                release_room_lock(rid, booking.checkin, booking.checkout)

            booking.status = "cancelled"
            session.commit()
            raise Exception("Booking đã hết hạn — không thể thanh toán")

        # Payment success
        payment.status = "completed"

        # Tạo booked_room
        for rid in booking.selected_rooms:
            BookedRoomRepository.create(
                session=session,
                booking_id=booking.id,
                room_id=rid,
                checkin=booking.checkin,
                checkout=booking.checkout
            )
            release_room_lock(rid, booking.checkin, booking.checkout)

        booking.status = "confirmed"
        session.commit()

        return {
            "message": "Thanh toán thành công",
            "booking_id": booking.id,
            "status": "confirmed"
        }
