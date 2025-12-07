from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, Enum as SQLEnum
from app.utils.enums import UserRole


class User(SQLModel, table=True):
    __tablename__ = "user"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True, nullable=False)
    password_hash: str = Field(nullable=False)
    full_name: str
    phone: Optional[str] = None

    # Role: super_admin | staff | customer
    role: UserRole = Field(
        default=UserRole.customer,
        sa_column=Column(SQLEnum(UserRole, name="user_role_enum"), nullable=False)
    )

    # Staff belongs to a property (customer/super_admin = None)
    property_id: Optional[int] = Field(
        default=None,
        foreign_key="property.id",
        nullable=True
    )

    is_active: bool = True

    # Relations
    bookings: List["Booking"] = Relationship(back_populates="user")
    reviews: List["Review"] = Relationship(back_populates="user")
