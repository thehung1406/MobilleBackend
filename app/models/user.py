from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, Enum as SQLEnum
from app.utils.enums import UserRole

if TYPE_CHECKING:
    from .booking import Booking
    from .review import Review


class User(SQLModel, table=True):
    __tablename__ = "user"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, nullable=False, index=True)
    password_hash: str = Field(nullable=False)
    full_name: str
    phone: Optional[str] = None

    role: UserRole = Field(
        default=UserRole.CUSTOMER,
        sa_column=Column(SQLEnum(UserRole, name="user_role_enum"), nullable=False)
    )

    property_id: Optional[int] = Field(
        default=None,
        foreign_key="property.id",
        nullable=True
    )

    is_active: bool = True

    # RELATIONSHIPS
    bookings: List["Booking"] = Relationship(back_populates="user")
    reviews: List["Review"] = Relationship(back_populates="user")
