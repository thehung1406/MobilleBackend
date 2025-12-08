from sqlmodel import Session, select
from app.models.property import Property


class PropertyRepository:

    # -----------------------
    # CREATE
    # -----------------------
    def create(self, session: Session, data: dict) -> Property:
        obj = Property(**data)
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj

    # -----------------------
    # GET BY ID
    # -----------------------
    def get(self, session: Session, prop_id: int) -> Property | None:
        return session.get(Property, prop_id)

    # -----------------------
    # LIST ALL
    # -----------------------
    def list_all(self, session: Session):
        return session.exec(select(Property)).all()

    # -----------------------
    # LIST ACTIVE (PUBLIC)
    # -----------------------
    def list_active(self, session: Session):
        stmt = select(Property).where(Property.is_active == True)
        return session.exec(stmt).all()

    # -----------------------
    # SEARCH PUBLIC
    # -----------------------
    def search(self, session: Session, keyword: str):
        key = f"%{keyword}%"

        stmt = (
            select(Property)
            .where(
                Property.is_active == True,
                (
                    Property.name.ilike(key)
                    | Property.address.ilike(key)
                    | Property.province.ilike(key)
                )
            )
            .order_by(Property.province, Property.name)
        )

        return session.exec(stmt).all()

    # -----------------------
    # UPDATE
    # -----------------------
    def update(self, session: Session, prop: Property, data: dict) -> Property:
        for field, value in data.items():
            if value is not None:
                setattr(prop, field, value)

        session.add(prop)
        session.commit()
        session.refresh(prop)
        return prop

    # -----------------------
    # DELETE
    # -----------------------
    def delete(self, session: Session, prop: Property):
        session.delete(prop)
        session.commit()
