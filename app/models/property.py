from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .room_type import RoomType
    from .review import Review
    from .property_amenity import PropertyAmenity


class Property(SQLModel, table=True):
    __tablename__ = "property"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: Optional[str] = None
    address: Optional[str] = None
    is_active: bool = True
    checkin: Optional[str] = None
    checkout: Optional[str] = None
    contact: Optional[str] = None
    image: Optional[str] = None
    cancel_policy: Optional[str] = None

    # RELATIONS
    room_types: List["RoomType"] = Relationship(back_populates="property")
    reviews: List["Review"] = Relationship(back_populates="property")
    amenities: List["PropertyAmenity"] = Relationship(back_populates="property")
