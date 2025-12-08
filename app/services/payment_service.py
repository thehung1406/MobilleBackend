from sqlmodel import Session
from fastapi import HTTPException
from datetime import datetime

from app.models.payment import Payment
from app.models.booking import Booking
from app.repositories.payment_repo import PaymentRepository
from app.services.mail_service import MailService
from app.utils.enums import BookingStatus  # nếu bạn có enum
from app.core.logger import logger


class PaymentService:

    def __init__(self):
        self.repo = PaymentRepository()
        self.mail = MailService()

    # ============================================================
    # CREATE PAYMENT (User click "Thanh toán")
    # ============================================================
    def create_payment(self, session: Session, booking_id: int, amount: float):

        if amount <= 0:
            raise HTTPException(400, "Amount must be > 0")

        booking = session.get(Booking, booking_id)

        if not booking:
            raise HTTPException(404, "Booking not found")

        if booking.status != BookingStatus.PENDING.value:
            raise HTTPException(400, "Booking is not pending")

        payment = Payment(
            booking_id=booking_id,
            amount=amount,
            status="pending"
        )

        payment = self.repo.create(session, payment)

        logger.info(f"[Payment] Created pending payment #{payment.id} for booking #{booking_id}")

        return payment

    # ============================================================
    # CONFIRM PAYMENT (Webhook từ cổng thanh toán)
    # ============================================================
    def confirm_webhook_payment(self, session: Session, payment_id: int):
        payment = self.repo.get(session, payment_id)

        if not payment:
            raise HTTPException(404, "Payment not found")

        # Prevent double payment
        if payment.status == "paid":
            logger.warning(f"[Payment] Payment #{payment.id} already processed")
            return payment

        booking = session.get(Booking, payment.booking_id)
        if not booking:
            raise HTTPException(404, "Booking related to payment not found")

        # Update payment
        payment.status = "paid"
        payment.payment_time = datetime.utcnow()

        # Update booking status
        booking.status = BookingStatus.PAID.value
        booking.expires_at = None  # không cho expire nữa

        session.commit()
        session.refresh(payment)
        session.refresh(booking)

        logger.info(f"[Payment] Payment confirmed #{payment.id} - Booking #{booking.id} marked as PAID")

        # Send email
        try:
            self.mail.send_payment_success(booking.id)
        except Exception as e:
            logger.error(f"[Payment] Failed to send payment email: {e}")

        return payment
