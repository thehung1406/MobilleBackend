# app/repositories/room_type_repo.py
from sqlmodel import Session, select
from app.models.room_type import RoomType


class RoomTypeRepository:

    # ----------------------------
    # CREATE
    # ----------------------------
    def create(self, session: Session, obj: RoomType):
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj

    # ----------------------------
    # READ
    # ----------------------------
    def get(self, session: Session, room_type_id: int):
        return session.get(RoomType, room_type_id)

    def list_all(self, session: Session):
        return session.exec(select(RoomType)).all()

    def list_by_property(self, session: Session, property_id: int):
        stmt = select(RoomType).where(RoomType.property_id == property_id)
        return session.exec(stmt).all()

    def list_active_by_property(self, session: Session, property_id: int):
        stmt = (
            select(RoomType)
            .where(RoomType.property_id == property_id)
            .where(RoomType.is_active == True)
        )
        return session.exec(stmt).all()

    def list_active(self, session: Session):
        stmt = select(RoomType).where(RoomType.is_active == True)
        return session.exec(stmt).all()

    # ----------------------------
    # UPDATE
    # ----------------------------
    def update(self, session: Session, obj: RoomType):
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj

    # ----------------------------
    # DELETE (HARD)
    # ----------------------------
    def delete(self, session: Session, obj: RoomType):
        session.delete(obj)
        session.commit()

    # ----------------------------
    # SOFT DELETE (RECOMMENDED)
    # ----------------------------
    def soft_delete(self, session: Session, obj: RoomType):
        obj.is_active = False
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj
