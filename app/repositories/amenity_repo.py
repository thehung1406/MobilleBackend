from sqlmodel import Session, select
from app.models.amenity import Amenity


class AmenityRepository:

    def create(self, session: Session, data: dict) -> Amenity:
        obj = Amenity(**data)
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj

    def get(self, session: Session, amenity_id: int):
        return session.get(Amenity, amenity_id)

    def list(self, session: Session):
        return session.exec(select(Amenity)).all()

    def update(self, session: Session, amenity_id: int, data: dict):
        obj = self.get(session, amenity_id)
        for k, v in data.items():
            setattr(obj, k, v)
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj

    def delete(self, session: Session, amenity_id: int):
        obj = self.get(session, amenity_id)
        session.delete(obj)
        session.commit()
        return True
