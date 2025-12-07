from sqlmodel import Session
from app.schemas.amenity import AmenityCreate, AmenityUpdate
from app.repositories.amenity_repo import AmenityRepository


class AmenityService:

    def __init__(self):
        self.repo = AmenityRepository()

    def create(self, session: Session, data: AmenityCreate):
        return self.repo.create(session, data.model_dump())

    def list(self, session: Session):
        return self.repo.list(session)

    def update(self, session: Session, amenity_id: int, data: AmenityUpdate):
        return self.repo.update(session, amenity_id, data.model_dump(exclude_unset=True))

    def delete(self, session: Session, amenity_id: int):
        return self.repo.delete(session, amenity_id)
