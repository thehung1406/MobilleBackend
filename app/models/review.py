from typing import Optional
from sqlmodel import SQLModel, Field, Relationship


class Review(SQLModel, table=True):
    __tablename__ = "review"

    id: Optional[int] = Field(default=None, primary_key=True)

    property_id: int = Field(foreign_key="property.id", index=True)
    user_id: int = Field(foreign_key="user.id", index=True)

    rating: int
    description: Optional[str] = None

    user: "User" = Relationship(back_populates="reviews")
    property: "Property" = Relationship(back_populates="reviews")
