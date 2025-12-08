from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.schemas.property_search import PropertySearchRequest, PropertySearchResponse
from app.services.property_search_service import PropertySearchService
from app.core.database import get_session

router = APIRouter(prefix="/properties", tags=["Public Properties"])
service = PropertySearchService()


@router.post("/search", response_model=PropertySearchResponse)
def search_properties(
    payload: PropertySearchRequest,
    session: Session = Depends(get_session),
):
    keyword = payload.keyword.strip()

    if not keyword:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Keyword must not be empty"
        )

    results = service.search_properties(session, keyword)

    return PropertySearchResponse(results=results)
