from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.services.payment_service import PaymentService
from app.utils.dependencies import get_session

router = APIRouter(prefix="/webhook/payment", tags=["Webhook"])

service = PaymentService()


@router.post("/{payment_id}")
def payment_webhook(payment_id: int, session: Session = Depends(get_session)):
    """
    Fake gateway callback:
    Gọi endpoint này chính là xác nhận thanh toán thành công.
    """
    result = service.confirm_webhook_payment(session, payment_id)
    return {"message": "Payment success", "payment": result}
