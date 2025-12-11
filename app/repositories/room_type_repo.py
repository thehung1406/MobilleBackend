from sqlmodel import Session, select
from app.models.room_type import RoomType


class RoomTypeRepository:

    @staticmethod
    def get_by_id(session: Session, room_type_id: int):
        stmt = select(RoomType).where(RoomType.id == room_type_id)
        return session.exec(stmt).first()

    @staticmethod
    def get_by_property(session: Session, property_id: int):
        stmt = select(RoomType).where(RoomType.property_id == property_id)
        return session.exec(stmt).all()
