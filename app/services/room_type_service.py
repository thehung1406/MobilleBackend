from sqlmodel import Session
from app.models.room_type import RoomType
from app.schemas.room_type import RoomTypeCreate, RoomTypeUpdate
from app.repositories.room_type_repo import RoomTypeRepository


class RoomTypeService:

    def __init__(self):
        self.repo = RoomTypeRepository()

    def create(self, session: Session, data: RoomTypeCreate):
        room_type = RoomType(**data.model_dump())
        return self.repo.create(session, room_type)

    def get(self, session: Session, room_type_id: int):
        obj = self.repo.get(session, room_type_id)
        if not obj:
            raise ValueError("Room type not found")
        return obj

    def list_all(self, session: Session):
        return self.repo.list_all(session)

    def list_by_property(self, session: Session, property_id: int):
        return self.repo.list_by_property(session, property_id)

    def update(self, session: Session, room_type_id: int, data: RoomTypeUpdate):
        obj = self.get(session, room_type_id)

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(obj, key, value)

        return self.repo.update(session, obj)

    def delete(self, session: Session, room_type_id: int):
        obj = self.get(session, room_type_id)
        self.repo.delete(session, obj)
        return True
