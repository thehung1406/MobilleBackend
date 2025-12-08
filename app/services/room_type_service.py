from fastapi import HTTPException, status
from sqlmodel import Session
from app.models.room_type import RoomType
from app.models.property import Property
from app.schemas.room_type import RoomTypeCreate, RoomTypeUpdate
from app.repositories.room_type_repo import RoomTypeRepository


class RoomTypeService:

    def __init__(self):
        self.repo = RoomTypeRepository()

    # CREATE
    def create(self, session: Session, data: RoomTypeCreate):

        # Kiểm tra property tồn tại (quan trọng)
        prop = session.get(Property, data.property_id)
        if not prop:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Property does not exist"
            )

        room_type = RoomType(**data.model_dump())
        return self.repo.create(session, room_type)

    # GET ONE
    def get(self, session: Session, room_type_id: int):
        obj = self.repo.get(session, room_type_id)
        if not obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Room type not found"
            )
        return obj

    # LIST ALL
    def list_all(self, session: Session):
        return self.repo.list_all(session)

    # LIST BY PROPERTY
    def list_by_property(self, session: Session, property_id: int):
        return self.repo.list_by_property(session, property_id)

    # UPDATE
    def update(self, session: Session, room_type_id: int, data: RoomTypeUpdate):
        obj = self.get(session, room_type_id)

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(obj, key, value)

        return self.repo.update(session, obj)

    # DELETE
    def delete(self, session: Session, room_type_id: int):
        obj = self.get(session, room_type_id)
        self.repo.delete(session, obj)
        return True
