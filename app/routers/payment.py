from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.schemas.payment import PaymentCreate, PaymentRead
from app.services.payment_service import PaymentService
from app.utils.dependencies import get_current_user, get_session

router = APIRouter(prefix="/payment", tags=["Payment"])
service = PaymentService()

@router.post("", response_model=PaymentRead)
def create_payment(
    payload: PaymentCreate,
    user = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    return service.create_payment(session, payload.booking_id, payload.amount)
