from sqlmodel import Session
from app.models.payment import Payment


class PaymentRepository:

    @staticmethod
    def create(session: Session, booking_id: int, amount: float, payment_type: str):
        payment = Payment(
            booking_id=booking_id,
            amount=amount,
            payment_type=payment_type,
            status="pending"
        )
        session.add(payment)
        session.commit()
        session.refresh(payment)
        return payment

    @staticmethod
    def get_by_id(session: Session, payment_id: int):
        return session.get(Payment, payment_id)

    @staticmethod
    def update_status(session: Session, payment_id: int, status: str):
        payment = session.get(Payment, payment_id)
        if not payment:
            return None
        payment.status = status
        session.commit()
        session.refresh(payment)
        return payment
