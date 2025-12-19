from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime

if TYPE_CHECKING:
    from .booking import Booking


class Payment(SQLModel, table=True):
    __tablename__ = "payment"

    id: Optional[int] = Field(default=None, primary_key=True)
    booking_id: int = Field(foreign_key="booking.id")

    amount: float
    payment_type: str
    status: str = "pending"
    payment_time: Optional[datetime] = None


    booking: "Booking" = Relationship(back_populates="payment")
