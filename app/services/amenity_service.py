from fastapi import HTTPException, status
from sqlmodel import Session

from app.schemas.amenity import AmenityCreate, AmenityUpdate
from app.repositories.amenity_repo import AmenityRepository
from app.core.logger import logger


class AmenityService:

    def __init__(self):
        self.repo = AmenityRepository()

    # ---------------------------------------------------
    # CREATE AMENITY
    # ---------------------------------------------------
    def create(self, session: Session, data: AmenityCreate):
        new_amenity = self.repo.create(session, data.model_dump())
        logger.info(f"[Amenity] Created amenity #{new_amenity.id}")
        return new_amenity

    # ---------------------------------------------------
    # LIST AMENITIES
    # ---------------------------------------------------
    def list(self, session: Session):
        return self.repo.list(session)

    # ---------------------------------------------------
    # UPDATE AMENITY
    # ---------------------------------------------------
    def update(self, session: Session, amenity_id: int, data: AmenityUpdate):

        amenity = self.repo.get(session, amenity_id)
        if not amenity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Amenity not found"
            )

        updated = self.repo.update(
            session,
            amenity_id,
            data.model_dump(exclude_unset=True)
        )

        logger.info(f"[Amenity] Updated amenity #{amenity_id}")
        return updated

    # ---------------------------------------------------
    # DELETE AMENITY
    # ---------------------------------------------------
    def delete(self, session: Session, amenity_id: int):

        amenity = self.repo.get(session, amenity_id)
        if not amenity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Amenity not found"
            )

        self.repo.delete(session, amenity_id)

        logger.info(f"[Amenity] Deleted amenity #{amenity_id}")
        return {"message": "Deleted successfully"}
