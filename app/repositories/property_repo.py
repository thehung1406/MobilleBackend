from sqlmodel import Session, select
from app.models.property import Property


class PropertyRepository:

    def create(self, session: Session, data: Property):
        session.add(data)
        session.commit()
        session.refresh(data)
        return data

    def get(self, session: Session, prop_id: int):
        return session.get(Property, prop_id)

    def list_all(self, session: Session):
        stmt = select(Property)
        return session.exec(stmt).all()

    def update(self, session: Session, prop: Property):
        session.add(prop)
        session.commit()
        session.refresh(prop)
        return prop

    def delete(self, session: Session, prop: Property):
        session.delete(prop)
        session.commit()
