from fastapi import HTTPException, status
from sqlmodel import Session

from app.schemas.property_amenity import PropertyAmenityCreate
from app.repositories.property_amenity_repo import PropertyAmenityRepository
from app.models.property import Property
from app.models.amenity import Amenity
from app.models.property_amenity import PropertyAmenity


class PropertyAmenityService:

    def __init__(self):
        self.repo = PropertyAmenityRepository()

    # ============================================================
    # ADD AMENITY TO PROPERTY
    # ============================================================
    def add(self, session: Session, data: PropertyAmenityCreate):

        # Validate property
        property_obj = session.get(Property, data.property_id)
        if not property_obj:
            raise HTTPException(404, "Property not found")

        # Validate amenity
        amenity_obj = session.get(Amenity, data.amenity_id)
        if not amenity_obj:
            raise HTTPException(404, "Amenity not found")

        # Check duplicate
        exists = session.exec(
            session.query(PropertyAmenity)
            .filter(
                PropertyAmenity.property_id == data.property_id,
                PropertyAmenity.amenity_id == data.amenity_id
            )
        ).first()

        if exists:
            raise HTTPException(
                status_code=400,
                detail="Amenity already assigned to this property"
            )

        return self.repo.add(session, data.model_dump())

    # ============================================================
    # LIST AMENITIES OF PROPERTY
    # ============================================================
    def list_by_property(self, session: Session, property_id: int):

        # Check property exists
        property_obj = session.get(Property, property_id)
        if not property_obj:
            raise HTTPException(404, "Property not found")

        return self.repo.list_by_property(session, property_id)

    # ============================================================
    # REMOVE AMENITY
    # ============================================================
    def remove(self, session: Session, pa_id: int):
        obj = session.get(PropertyAmenity, pa_id)
        if not obj:
            raise HTTPException(404, "PropertyAmenity not found")

        return self.repo.remove(session, pa_id)
