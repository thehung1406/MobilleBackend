from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class PaymentCreate(BaseModel):
    booking_id: int
    amount: float
    payment_type: str      # momo / vnpay / stripe / cash

class PaymentRead(BaseModel):
    id: int
    booking_id: int
    amount: float
    payment_type: str
    status: str
    payment_time: Optional[datetime] = None

    class Config:
        from_attributes = True
