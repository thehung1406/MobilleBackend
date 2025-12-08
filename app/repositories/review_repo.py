from sqlmodel import Session, select
from app.models.review import Review


class ReviewRepository:

    # ---------------- CREATE ----------------
    def create(self, session: Session, data: dict) -> Review:
        obj = Review(**data)
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj

    # ---------------- LIST BY PROPERTY ----------------
    def list_by_property(self, session: Session, property_id: int):
        stmt = (
            select(Review)
            .where(Review.property_id == property_id)
            .order_by(Review.id.desc())
        )
        return session.exec(stmt).all()

    # ---------------- GET ----------------
    def get(self, session: Session, review_id: int) -> Review | None:
        return session.get(Review, review_id)

    # ---------------- UPDATE ----------------
    def update(self, session: Session, review_id: int, data: dict):
        obj = self.get(session, review_id)
        if not obj:
            return None  # tránh lỗi NoneType

        for k, v in data.items():
            if v is not None:
                setattr(obj, k, v)

        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj

    # ---------------- DELETE ----------------
    def delete(self, session: Session, review_id: int) -> bool:
        obj = self.get(session, review_id)
        if not obj:
            return False

        session.delete(obj)
        session.commit()
        return True
