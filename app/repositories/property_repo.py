from sqlmodel import Session, select
from app.models.property import Property


class PropertyRepository:

    @staticmethod
    def get_by_id(session: Session, property_id: int):
        statement = select(Property).where(Property.id == property_id)
        return session.exec(statement).first()
