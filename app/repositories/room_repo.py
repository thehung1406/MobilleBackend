from sqlmodel import Session, select
from app.models.room import Room


class RoomRepository:

    def create(self, session: Session, data: dict) -> Room:
        obj = Room(**data)
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj

    def get(self, session: Session, room_id: int) -> Room:
        return session.get(Room, room_id)

    def list_all(self, session: Session):
        return session.exec(select(Room)).all()

    def list_by_property(self, session: Session, prop_id: int):
        return session.exec(select(Room).where(Room.property_id == prop_id)).all()

    def update(self, session: Session, room_id: int, data: dict):
        obj = self.get(session, room_id)
        for k, v in data.items():
            setattr(obj, k, v)
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj

    def delete(self, session: Session, room_id: int):
        obj = self.get(session, room_id)
        session.delete(obj)
        session.commit()
        return True
