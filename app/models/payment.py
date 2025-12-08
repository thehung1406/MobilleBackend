from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field, Relationship


class Payment(SQLModel, table=True):
    __tablename__ = "payment"

    id: Optional[int] = Field(default=None, primary_key=True)
    booking_id: int = Field(foreign_key="booking.id")

    amount: float
    payment_type: str = "fake_gateway"
    status: str = "pending"
    payment_time: Optional[datetime] = None

    booking: "Booking" = Relationship(back_populates="payment")
