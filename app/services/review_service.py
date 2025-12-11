from sqlmodel import Session
from app.models.review import Review
from app.repositories.review_repo import ReviewRepository
from app.schemas.review import ReviewCreate, ReviewRead


class ReviewService:

    @staticmethod
    def add_review(session: Session, user_id: int, data: ReviewCreate):
        review = Review(
            property_id=data.property_id,
            user_id=user_id,
            rating=data.rating,
            description=data.description
        )
        created = ReviewRepository.create(session, review)
        return ReviewRead(
            id=created.id,
            user_id=created.user_id,
            rating=created.rating,
            description=created.description
        )

    @staticmethod
    def get_reviews_for_property(session: Session, property_id: int):
        rows = ReviewRepository.get_by_property(session, property_id)

        results = []
        for review, user in rows:
            results.append(
                ReviewRead(
                    id=review.id,
                    user_id=review.user_id,
                    rating=review.rating,
                    description=review.description,
                    user_name=user.full_name or user.email
                )
            )
        return results

    @staticmethod
    def delete_review(session: Session, review_id: int):
        review = ReviewRepository.get_by_id(session, review_id)
        if not review:
            raise Exception("Review không tồn tại")

        ReviewRepository.delete(session, review)
        return True

