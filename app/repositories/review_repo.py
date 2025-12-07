from sqlmodel import Session, select
from app.models.review import Review

class ReviewRepository:

    def create(self, session: Session, data: dict):
        obj = Review(**data)
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj

    def list_by_property(self, session: Session, property_id: int):
        return session.exec(
            select(Review)
            .where(Review.property_id == property_id)
            .order_by(Review.id.desc())
        ).all()

    def get(self, session: Session, review_id: int):
        return session.get(Review, review_id)

    def update(self, session: Session, review_id: int, data: dict):
        obj = self.get(session, review_id)
        for k, v in data.items():
            setattr(obj, k, v)
        session.commit()
        session.refresh(obj)
        return obj

    def delete(self, session: Session, review_id: int):
        obj = self.get(session, review_id)
        session.delete(obj)
        session.commit()
