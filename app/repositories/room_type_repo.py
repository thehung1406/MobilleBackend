from sqlmodel import Session, select
from app.models.room_type import RoomType


class RoomTypeRepository:

    def create(self, session: Session, obj: RoomType):
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj

    def get(self, session: Session, room_type_id: int):
        return session.get(RoomType, room_type_id)

    def list_by_property(self, session: Session, property_id: int):
        stmt = select(RoomType).where(RoomType.property_id == property_id)
        return session.exec(stmt).all()

    def list_all(self, session: Session):
        stmt = select(RoomType)
        return session.exec(stmt).all()

    def update(self, session: Session, obj: RoomType):
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj

    def delete(self, session: Session, obj: RoomType):
        session.delete(obj)
        session.commit()

    def list_active(self, session: Session):
        return session.exec(select(RoomType).where(RoomType.is_active == True)).all()

