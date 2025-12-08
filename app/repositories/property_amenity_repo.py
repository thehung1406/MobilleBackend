from sqlmodel import Session, select
from app.models.property_amenity import PropertyAmenity


class PropertyAmenityRepository:

    # -------------------------
    # CREATE
    # -------------------------
    def add(self, session: Session, data: dict) -> PropertyAmenity:
        obj = PropertyAmenity(**data)
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj

    # -------------------------
    # CHECK EXISTING RELATION
    # -------------------------
    def exists(self, session: Session, property_id: int, amenity_id: int) -> bool:
        stmt = (
            select(PropertyAmenity)
            .where(
                PropertyAmenity.property_id == property_id,
                PropertyAmenity.amenity_id == amenity_id,
            )
        )
        return session.exec(stmt).first() is not None

    # -------------------------
    # LIST AMENITIES BY PROPERTY
    # -------------------------
    def list_by_property(self, session: Session, property_id: int):
        stmt = select(PropertyAmenity).where(PropertyAmenity.property_id == property_id)
        return session.exec(stmt).all()

    # -------------------------
    # REMOVE BY PRIMARY ID
    # -------------------------
    def remove(self, session: Session, pa_id: int) -> bool:
        obj = session.get(PropertyAmenity, pa_id)
        if not obj:
            return False
        session.delete(obj)
        session.commit()
        return True

    # -------------------------
    # REMOVE BY (PROPERTY, AMENITY)
    # -------------------------
    def remove_pair(self, session: Session, property_id: int, amenity_id: int) -> bool:
        stmt = (
            select(PropertyAmenity)
            .where(
                PropertyAmenity.property_id == property_id,
                PropertyAmenity.amenity_id == amenity_id,
            )
        )
        obj = session.exec(stmt).first()
        if not obj:
            return False
        session.delete(obj)
        session.commit()
        return True
