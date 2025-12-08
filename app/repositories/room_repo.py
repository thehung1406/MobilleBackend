from sqlmodel import Session, select
from app.models.room import Room
from app.models.room_type import RoomType


class RoomRepository:

    # ---------------- CREATE ----------------
    def create(self, session: Session, data: dict) -> Room:
        obj = Room(**data)
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj

    # ---------------- GET ----------------
    def get(self, session: Session, room_id: int) -> Room:
        return session.get(Room, room_id)

    # ---------------- LIST ALL ----------------
    def list_all(self, session: Session):
        return session.exec(select(Room)).all()

    # ---------------- LIST BY PROPERTY (FIXED) ----------------
    def list_by_property(self, session: Session, prop_id: int):
        stmt = (
            select(Room)
            .join(RoomType, Room.room_type_id == RoomType.id)
            .where(RoomType.property_id == prop_id)
        )
        return session.exec(stmt).all()

    # ---------------- UPDATE ----------------
    def update(self, session: Session, room_id: int, data: dict):
        obj = self.get(session, room_id)
        if not obj:
            return None

        for k, v in data.items():
            setattr(obj, k, v)

        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj

    # ---------------- DELETE ----------------
    def delete(self, session: Session, room_id: int):
        obj = self.get(session, room_id)
        if not obj:
            return False

        session.delete(obj)
        session.commit()
        return True
