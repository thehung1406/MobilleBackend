from sqlmodel import Session, select
from app.models.property import Property


class PropertySearchRepository:

    def search(self, session: Session, keyword: str):
        """
        Search khách sạn theo:
        - name
        - address
        - province
        (case insensitive, public search)
        """

        # Nếu người dùng không nhập gì → trả về toàn bộ active property
        if not keyword or keyword.strip() == "":
            stmt = (
                select(Property)
                .where(Property.is_active == True)
                .order_by(Property.province, Property.name)
            )
            return session.exec(stmt).all()

        key = f"%{keyword}%"

        stmt = (
            select(Property)
            .where(
                Property.is_active == True,
                (
                    Property.name.ilike(key) |
                    Property.address.ilike(key) |
                    Property.province.ilike(key)
                )
            )
            .order_by(Property.province, Property.name)
        )

        return session.exec(stmt).all()
