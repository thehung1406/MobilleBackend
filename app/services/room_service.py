from sqlmodel import Session
from app.repositories.room_repo import RoomRepository


class RoomService:

    @staticmethod
    def check_availability(session: Session, room_id: int, checkin, checkout):
        return RoomRepository.is_available(session, room_id, checkin, checkout)
