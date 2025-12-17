from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.core.database import get_session
from app.services.property_service import PropertyService
from app.schemas.property import PropertyRead

router = APIRouter(prefix="/properties", tags=["Property"])


@router.get("", response_model=list[PropertyRead])
def list_properties(session: Session = Depends(get_session)):
    return PropertyService.list_properties(session)
