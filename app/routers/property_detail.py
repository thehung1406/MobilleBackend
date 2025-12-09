from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.core.database import get_session
from app.schemas.property_detail import PropertyDetailRead
from app.services.property_service import PropertyService

router = APIRouter(prefix="/properties", tags=["Properties"])


@router.get("/{property_id}", response_model=PropertyDetailRead)
def get_detail(property_id: int, session: Session = Depends(get_session)):
    result = PropertyService.get_detail(session, property_id)
    if not result:
        raise HTTPException(404, "Property not found")
    return result
