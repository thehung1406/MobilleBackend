from pydantic import BaseModel
import uuid

class PaymentCreate(BaseModel):
    booking_id: uuid.UUID
    method: str = "card"

class PaymentOut(BaseModel):
    id: uuid.UUID
    booking_id: uuid.UUID
    amount: float
    method: str
    status: str
    transaction_code: str | None = None
