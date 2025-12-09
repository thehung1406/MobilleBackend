# app/routers/property_search.py
from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.core.database import get_session
from app.schemas.property_search import PropertySearchRequest, PropertySearchResponse
from app.services.property_search_service import PropertySearchService

router = APIRouter(prefix="/search", tags=["Search"])


@router.post("/property", response_model=PropertySearchResponse)
def search_property(payload: PropertySearchRequest, session: Session = Depends(get_session)):
    return PropertySearchService.search(session, payload.keyword)
