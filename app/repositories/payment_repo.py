from sqlmodel import Session, select
from app.models.payment import Payment


class PaymentRepository:

    # -------------------------
    # CREATE PAYMENT
    # -------------------------
    def create(self, session: Session, payment: Payment) -> Payment:
        session.add(payment)
        session.commit()
        session.refresh(payment)
        return payment

    # -------------------------
    # GET PAYMENT BY ID
    # -------------------------
    def get(self, session: Session, payment_id: int) -> Payment | None:
        return session.get(Payment, payment_id)

    # -------------------------
    # LIST PAYMENTS BY BOOKING
    # -------------------------
    def list_by_booking(self, session: Session, booking_id: int):
        stmt = select(Payment).where(Payment.booking_id == booking_id)
        return session.exec(stmt).all()

    # -------------------------
    # UPDATE PAYMENT OBJECT
    # -------------------------
    def update(self, session: Session, payment: Payment) -> Payment:
        session.add(payment)
        session.commit()
        session.refresh(payment)
        return payment

    # -------------------------
    # UPDATE PAYMENT STATUS ONLY
    # -------------------------
    def update_status(self, session: Session, payment_id: int, status: str):
        payment = self.get(session, payment_id)
        if not payment:
            return None

        payment.status = status
        session.add(payment)
        session.commit()
        session.refresh(payment)
        return payment
