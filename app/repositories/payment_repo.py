from sqlmodel import Session
from app.models.payment import Payment

class PaymentRepository:

    def create(self, session: Session, payment: Payment):
        session.add(payment)
        session.commit()
        session.refresh(payment)
        return payment

    def update(self, session: Session, payment: Payment):
        session.add(payment)
        session.commit()
        session.refresh(payment)
        return payment

    def get(self, session: Session, payment_id: int):
        return session.get(Payment, payment_id)
