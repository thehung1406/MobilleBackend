from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship

from app.models.property_amenity import PropertyAmenity


class Amenity(SQLModel, table=True):
    __tablename__ = "amenity"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: Optional[str] = None

    property_amenities: List["PropertyAmenity"] = Relationship(back_populates="amenity")
