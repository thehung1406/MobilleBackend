from sqlmodel import Session
from app.models.property import Property
from app.schemas.property import PropertyCreate, PropertyUpdate
from app.repositories.property_repo import PropertyRepository


class PropertyService:

    def __init__(self):
        self.repo = PropertyRepository()

    def create_property(self, session: Session, data: PropertyCreate):
        prop = Property(**data.model_dump())
        return self.repo.create(session, prop)

    def get_property(self, session: Session, prop_id: int):
        prop = self.repo.get(session, prop_id)
        if not prop:
            raise ValueError("Property not found")
        return prop

    def list_properties(self, session: Session):
        return self.repo.list_all(session)

    def update_property(self, session: Session, prop_id: int, data: PropertyUpdate):
        prop = self.get_property(session, prop_id)

        update_data = data.model_dump(exclude_unset=True)
        for key, val in update_data.items():
            setattr(prop, key, val)

        return self.repo.update(session, prop)

    def delete_property(self, session: Session, prop_id: int):
        prop = self.get_property(session, prop_id)
        self.repo.delete(session, prop)
        return True
