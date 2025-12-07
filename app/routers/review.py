from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.schemas.review import ReviewCreate, ReviewUpdate, ReviewRead
from app.services.review_service import ReviewService
from app.utils.dependencies import (
    get_current_user,
    require_customer,
    get_session
)

router = APIRouter(prefix="/review", tags=["Review"])
service = ReviewService()

# CUSTOMER tạo review
@router.post("", response_model=ReviewRead)
def create_review(
    data: ReviewCreate,
    user = Depends(require_customer),
    session: Session = Depends(get_session),
):
    return service.create(session, user, data)

# Public GET review
@router.get("/property/{property_id}", response_model=list[ReviewRead])
def list_reviews(property_id: int, session: Session = Depends(get_session)):
    return service.list_by_property(session, property_id)

# UPDATE — customer / staff / admin
@router.patch("/{review_id}", response_model=ReviewRead)
def update_review(
    review_id: int,
    data: ReviewUpdate,
    user = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    return service.update(session, review_id, user, data)

# DELETE — tất cả roles (service sẽ check quyền)
@router.delete("/{review_id}")
def delete_review(
    review_id: int,
    user = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    service.delete(session, review_id, user)
    return {"message": "Review deleted"}
