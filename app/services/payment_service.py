from sqlmodel import Session
from fastapi import HTTPException
from datetime import datetime

from app.models.payment import Payment
from app.models.booking import Booking
from app.repositories.payment_repo import PaymentRepository
from app.services.mail_service import MailService


class PaymentService:

    def __init__(self):
        self.repo = PaymentRepository()
        self.mail = MailService()

    def create_payment(self, session: Session, booking_id: int, amount: float):
        booking = session.get(Booking, booking_id)

        if not booking:
            raise HTTPException(404, "Booking not found")

        if booking.status != "pending":
            raise HTTPException(400, "Booking is not pending")

        payment = Payment(
            booking_id=booking_id,
            amount=amount,
            status="pending"
        )

        return self.repo.create(session, payment)

    def confirm_webhook_payment(self, session: Session, payment_id: int):
        payment = self.repo.get(session, payment_id)

        if not payment:
            raise HTTPException(404, "Payment not found")

        booking = session.get(Booking, payment.booking_id)

        payment.status = "paid"
        payment.payment_time = datetime.utcnow()
        booking.status = "paid"

        session.commit()
        session.refresh(payment)
        session.refresh(booking)

        self.mail.send_payment_success(booking.id)

        return payment
