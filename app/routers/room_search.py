from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.core.database import get_session
from app.schemas.room_search import RoomSearchRequest, RoomSearchResponse
from app.services.room_search_service import RoomSearchService

router = APIRouter(prefix="/rooms", tags=["Room Search"])
service = RoomSearchService()


@router.post("/search", response_model=RoomSearchResponse)
def search_rooms(
    payload: RoomSearchRequest,
    session: Session = Depends(get_session)
):
    return service.search_available_rooms(session, payload.model_dump())
