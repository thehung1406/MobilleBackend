from typing import Optional
from sqlmodel import SQLModel, Field, Relationship

from app.models import Property
from app.models.amenity import Amenity


class PropertyAmenity(SQLModel, table=True):
    __tablename__ = "property_amenity"

    id: Optional[int] = Field(default=None, primary_key=True)
    amenity_id: int = Field(foreign_key="amenity.id")
    property_id: int = Field(foreign_key="property.id")

    amenity: "Amenity" = Relationship(back_populates="property_amenities")
    property: "Property" = Relationship(back_populates="amenities")
