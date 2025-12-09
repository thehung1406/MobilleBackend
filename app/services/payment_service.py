import uuid
from sqlmodel import Session
from app.repositories.payment_repo import PaymentRepository
from app.repositories.booking_repo import BookingRepository
from app.utils.qr_generator import generate_qr_base64
from app.services.mail_service import MailService
from app.models.booking import Booking


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

        # QR code chứa payment_code hoặc booking_id
        qr_data = f"Thanh toán booking #{booking_id} | Code: {payment_code}"
        qr_base64 = generate_qr_base64(qr_data)

        return {
            "payment_id": payment.id,
            "booking_id": booking_id,
            "amount": amount,
            "payment_code": payment_code,
            "qr_base64": qr_base64,
            "status": "pending",
        }

    @staticmethod
    def confirm_payment(session: Session, payment_id: int):

        payment = PaymentRepository.get_by_id(session, payment_id)
        if not payment:
            raise Exception("Không tìm thấy payment")

        booking = session.get(Booking, payment.booking_id)
        if not booking:
            raise Exception("Booking không tồn tại")

        # update payment
        PaymentRepository.update_status(session, payment_id, "success")

        # update booking
        booking.status = "confirmed"
        session.add(booking)
        session.commit()

        # gửi email xác nhận thanh toán
        MailService().send_payment_success(booking.id)

        # gửi email xác nhận booking
        MailService().send_booking_confirmation(booking.id)

        return {
            "message": "Thanh toán thành công",
            "booking_id": booking.id,
            "status": "confirmed"
        }
