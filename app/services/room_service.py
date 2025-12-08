from sqlmodel import Session
from app.repositories.room_repo import RoomRepository
from app.schemas.room import RoomCreate, RoomUpdate


class RoomService:

    def __init__(self):
        self.repo = RoomRepository()

    # CREATE ROOM
    def create(self, session: Session, data: RoomCreate):
        return self.repo.create(session, data.model_dump())

    # GET ONE
    def get(self, session: Session, room_id: int):
        return self.repo.get(session, room_id)

    # LIST ALL ROOMS
    def list_all(self, session: Session):
        return self.repo.list_all(session)

    # LIST ROOMS BY PROPERTY (FIXED)
    def list_by_property(self, session: Session, property_id: int):
        return self.repo.list_by_property(session, property_id)

    # UPDATE ROOM
    def update(self, session: Session, room_id: int, data: RoomUpdate):
        return self.repo.update(session, room_id, data.model_dump(exclude_unset=True))

    # DELETE ROOM
    def delete(self, session: Session, room_id: int):
        return self.repo.delete(session, room_id)
