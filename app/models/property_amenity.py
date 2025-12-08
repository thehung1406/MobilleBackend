from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .amenity import Amenity
    from .property import Property


class PropertyAmenity(SQLModel, table=True):
    __tablename__ = "property_amenity"

    id: Optional[int] = Field(default=None, primary_key=True)
    amenity_id: int = Field(foreign_key="amenity.id")
    property_id: int = Field(foreign_key="property.id")

    amenity: "Amenity" = Relationship(back_populates="property_amenities")
    property: "Property" = Relationship(back_populates="amenities")
