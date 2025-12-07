from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PaymentCreate(BaseModel):
    booking_id: int
    amount: float

class PaymentRead(BaseModel):
    id: int
    booking_id: int
    amount: float
    status: str
    payment_time: Optional[datetime] = None   # FIX HERE

    class Config:
        from_attributes = True
