from sqlmodel import Session, select
from app.models.room_type import RoomType


class RoomTypeRepository:

    @staticmethod
    def get_by_property(session: Session, property_id: int):
        statement = select(RoomType).where(RoomType.property_id == property_id)
        return session.exec(statement).all()
