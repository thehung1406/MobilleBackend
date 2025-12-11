from sqlmodel import Session, select
from app.models.review import Review
from app.models.user import User


class ReviewRepository:

    @staticmethod
    def create(session: Session, review: Review):
        session.add(review)
        session.commit()
        session.refresh(review)
        return review

    @staticmethod
    def get_by_property(session: Session, property_id: int):
        stmt = (
            select(Review, User)
            .join(User, User.id == Review.user_id)
            .where(Review.property_id == property_id)
        )
        rows = session.exec(stmt).all()
        return rows

    @staticmethod
    def delete(session: Session, review: Review):
        session.delete(review)
        session.commit()
