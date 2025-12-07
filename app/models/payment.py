from typing import Optional
from datetime import date
from sqlmodel import SQLModel, Field, Relationship

from app.models import Booking


class Payment(SQLModel, table=True):
    __tablename__ = "payment"

    id: Optional[int] = Field(default=None, primary_key=True)
    booking_id: int = Field(foreign_key="booking.id")

    payment_date: date
    payment_type: str
    status: str

    booking: "Booking" = Relationship(back_populates="payment")
