# app/repositories/property_search_repo.py
from sqlmodel import Session, select
from app.models.property import Property


class PropertySearchRepository:

    @staticmethod
    def search_properties(session: Session, keyword: str):
        pattern = f"%{keyword}%"

        statement = (
            select(Property)
            .where(
                (Property.name.ilike(pattern)) |
                (Property.address.ilike(pattern))
            )
            .where(Property.is_active == True)
        )

        results = session.exec(statement).all()
        return results
