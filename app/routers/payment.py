from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.schemas.payment import PaymentCreate, PaymentRead
from app.services.payment_service import PaymentService
from app.utils.dependencies import get_current_user, get_session

router = APIRouter(prefix="/payment", tags=["Payment"])
service = PaymentService()


@router.post("", response_model=PaymentRead, status_code=status.HTTP_201_CREATED)
def create_payment(
    payload: PaymentCreate,
    user = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    CREATE PAYMENT
    --------------
    Public for CUSTOMER:
    - Chỉ được thanh toán booking của chính mình
    - Booking phải ở trạng thái pending
    """
    booking_id = payload.booking_id

    # Security: User chỉ thanh toán booking của họ
    booking = session.get(type(service).__dict__['repo'].model, booking_id) \
        or session.get_payment_booking(booking_id)  # fallback nếu cần

    if booking and booking.user_id != user.id:
        raise HTTPException(
            status_code=403,
            detail="Bạn không thể thanh toán booking của người khác"
        )

    return service.create_payment(
        session,
        booking_id=payload.booking_id,
        amount=payload.amount
    )
