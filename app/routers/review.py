from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.core.database import get_session
from app.schemas.review import ReviewCreate, ReviewRead
from app.services.review_service import ReviewService
from app.utils.dependencies import get_current_user, require_staff

router = APIRouter(prefix="/reviews", tags=["Review"])


@router.post("", response_model=ReviewRead)
def create_review(
    payload: ReviewCreate,
    session: Session = Depends(get_session),
    user=Depends(get_current_user)
):
    return ReviewService.add_review(session, user.id, payload)


@router.get("/property/{property_id}", response_model=list[ReviewRead])
def list_reviews(property_id: int, session: Session = Depends(get_session)):
    return ReviewService.get_reviews_for_property(session, property_id)



# ----------------------------------------------------
# XÓA review (only STAFF or ADMIN)
# ----------------------------------------------------
@router.delete("/{review_id}")
def delete_review(
    review_id: int,
    session: Session = Depends(get_session),
    staff=Depends(require_staff),
):
    try:
        ReviewService.delete_review(session, review_id)
        return {"status": "deleted"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
