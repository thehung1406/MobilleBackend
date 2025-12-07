from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship

from app.models import Booking
from app.models.review import Review


class User(SQLModel, table=True):
    __tablename__ = "user"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True, nullable=False)
    password_hash: str
    full_name: str
    phone: Optional[str] = None
    role: UserRole = Field(sa_column=Column(Enum(UserRole)))
    is_active: bool = True
    # Relationships
    bookings: List["Booking"] = Relationship(back_populates="user")
    reviews: List["Review"] = Relationship(back_populates="user")
