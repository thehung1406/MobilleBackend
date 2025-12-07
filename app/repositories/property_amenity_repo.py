from sqlmodel import Session, select
from app.models.property_amenity import PropertyAmenity


class PropertyAmenityRepository:

    def add(self, session: Session, data: dict):
        obj = PropertyAmenity(**data)
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj

    def list_by_property(self, session: Session, property_id: int):
        return session.exec(
            select(PropertyAmenity).where(PropertyAmenity.property_id == property_id)
        ).all()

    def remove(self, session: Session, pa_id: int):
        obj = session.get(PropertyAmenity, pa_id)
        session.delete(obj)
        session.commit()
        return True
