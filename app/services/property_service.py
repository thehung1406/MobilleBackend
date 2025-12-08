from fastapi import HTTPException
from sqlmodel import Session

from app.models.property import Property
from app.schemas.property import PropertyCreate, PropertyUpdate
from app.repositories.property_repo import PropertyRepository


class PropertyService:

    def __init__(self):
        self.repo = PropertyRepository()

    # ======================================================
    # CREATE PROPERTY
    # ======================================================
    def create_property(self, session: Session, data: PropertyCreate):

        # Normalize province (optional nhưng tốt cho search)
        province = (data.province.lower().strip()
                    if data.province else None)

        prop = Property(
            **data.model_dump(),
            province=province
        )

        return self.repo.create(session, prop)

    # ======================================================
    # GET PROPERTY
    # ======================================================
    def get_property(self, session: Session, prop_id: int) -> Property:
        prop = self.repo.get(session, prop_id)
        if not prop:
            raise HTTPException(404, "Property not found")
        return prop

    # ======================================================
    # LIST ALL (PUBLIC)
    # ======================================================
    def list_properties(self, session: Session):
        return [
            p for p in
            self.repo.list_all(session)
            if p.is_active
        ]

    # ======================================================
    # UPDATE PROPERTY
    # ======================================================
    def update_property(self, session: Session, prop_id: int, data: PropertyUpdate):
        prop = self.get_property(session, prop_id)

        update_data = data.model_dump(exclude_unset=True)

        # Normalize province again if provided
        if "province" in update_data and update_data["province"]:
            update_data["province"] = update_data["province"].lower().strip()

        for key, val in update_data.items():
            setattr(prop, key, val)

        return self.repo.update(session, prop)

    # ======================================================
    # DELETE PROPERTY
    # ======================================================
    def delete_property(self, session: Session, prop_id: int):
        prop = self.get_property(session, prop_id)
        self.repo.delete(session, prop)
        return True
