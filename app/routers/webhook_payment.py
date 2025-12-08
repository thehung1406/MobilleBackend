from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.schemas.payment import PaymentRead
from app.services.payment_service import PaymentService
from app.utils.dependencies import get_session

router = APIRouter(prefix="/webhook/payment", tags=["Webhook"])
service = PaymentService()


@router.post("/{payment_id}/confirm", response_model=PaymentRead)
def payment_webhook(
    payment_id: int,
    session: Session = Depends(get_session),
):
    """
    Webhook từ gateway thanh toán để xác nhận payment.
    Có thể gọi nhiều lần → service idempotent.
    """
    payment = service.confirm_webhook_payment(session, payment_id)
    return payment
