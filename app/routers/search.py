from fastapi import APIRouter
from app.schemas.search import SearchRequest, SearchResponse
from app.services.search_service import SearchService

router = APIRouter(prefix="/search", tags=["Search"])
service = SearchService()

@router.post("", response_model=SearchResponse)
def search_available_rooms(payload: SearchRequest):

    room_types = service.search_available_rooms(payload.model_dump())

    return SearchResponse(
        property_id=payload.property_id,
        checkin=payload.checkin,
        checkout=payload.checkout,
        room_types=room_types
    )
