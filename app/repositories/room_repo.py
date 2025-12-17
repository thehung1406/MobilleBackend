from sqlmodel import Session, select
from datetime import date
from app.models.room import Room
from app.models.booked_room import BookedRoom


class RoomRepository:

    @staticmethod
    def get_by_room_type(session: Session, room_type_id: int):
        statement = select(Room).where(Room.room_type_id == room_type_id)
        return session.exec(statement).all()

    @staticmethod
    def is_available(session: Session, room_id: int, checkin: date, checkout: date) -> bool:
        """
        TRUE nếu không có booking nào trùng ngày
        """
        statement = (
            select(BookedRoom)
            .where(BookedRoom.room_id == room_id)
            .where(BookedRoom.checkin < checkout)
            .where(BookedRoom.checkout > checkin)
        )
        conflict = session.exec(statement).first()
        return conflict is None
