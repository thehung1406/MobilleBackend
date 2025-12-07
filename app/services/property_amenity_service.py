from sqlmodel import Session
from app.schemas.property_amenity import PropertyAmenityCreate
from app.repositories.property_amenity_repo import PropertyAmenityRepository


class PropertyAmenityService:

    def __init__(self):
        self.repo = PropertyAmenityRepository()

    def add(self, session: Session, data: PropertyAmenityCreate):
        return self.repo.add(session, data.model_dump())

    def list_by_property(self, session: Session, property_id: int):
        return self.repo.list_by_property(session, property_id)

    def remove(self, session: Session, pa_id: int):
        return self.repo.remove(session, pa_id)
