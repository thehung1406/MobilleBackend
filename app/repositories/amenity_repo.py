from sqlmodel import Session, select
from app.models.amenity import Amenity


class AmenityRepository:

    # ---------------- CREATE ----------------
    def create(self, session: Session, data: dict) -> Amenity:
        obj = Amenity(**data)
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj

    # ---------------- GET ----------------
    def get(self, session: Session, amenity_id: int) -> Amenity | None:
        return session.get(Amenity, amenity_id)

    # ---------------- LIST ALL ----------------
    def list_all(self, session: Session):
        return session.exec(select(Amenity)).all()

    # ---------------- UPDATE ----------------
    def update(self, session: Session, amenity_id: int, data: dict):
        obj = self.get(session, amenity_id)
        if not obj:
            raise ValueError("Amenity not found")

        for k, v in data.items():
            setattr(obj, k, v)

        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj

    # ---------------- DELETE ----------------
    def delete(self, session: Session, amenity_id: int) -> bool:
        obj = self.get(session, amenity_id)
        if not obj:
            raise ValueError("Amenity not found")

        session.delete(obj)
        session.commit()
        return True
