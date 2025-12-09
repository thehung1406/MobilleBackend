from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.core.database import get_session

from app.schemas.payment import PaymentCreate
from app.services.payment_service import PaymentService

router = APIRouter(prefix="/payment", tags=["Payment"])


# 1) User nhấn "Thanh toán" → tạo payment + tạo QR
@router.post("")
def create_payment(payload: PaymentCreate, session: Session = Depends(get_session)):
    return PaymentService.create_payment(
        session=session,
        booking_id=payload.booking_id,
        amount=payload.amount,
        payment_type=payload.payment_type,
    )


# 2) User bấm nút "Tôi đã thanh toán"
@router.post("/{payment_id}/confirm")
def confirm_payment(payment_id: int, session: Session = Depends(get_session)):
    return PaymentService.confirm_payment(session=session, payment_id=payment_id)
