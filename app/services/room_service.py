from sqlmodel import Session
from app.repositories.room_repo import RoomRepository
from app.repositories.room_type_repo import RoomTypeRepository
from app.schemas.room import RoomRead


class RoomService:

    @staticmethod
    def get_available_rooms(session: Session, room_type_id: int, checkin, checkout):


        rt = RoomTypeRepository.get_by_id(session, room_type_id)
        if not rt:
            raise Exception("Room type không tồn tại")


        rooms = RoomRepository.get_by_room_type(session, room_type_id)


        available_rooms = []
        for room in rooms:
            if RoomRepository.is_available(session, room.id, checkin, checkout):
                available_rooms.append(RoomRead.from_orm(room))

        return available_rooms
