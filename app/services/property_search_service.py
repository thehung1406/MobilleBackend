# app/services/property_search_service.py
from sqlmodel import Session
from app.repositories.property_search_repo import PropertySearchRepository
from app.schemas.property_search import PropertyItem, PropertySearchResponse
from app.utils.redis_cache import r, make_key, cache_get, cache_set


class PropertySearchService:

    @staticmethod
    def search(session: Session, keyword: str) -> PropertySearchResponse:
        # -------------------
        # REDIS CACHE CHECK
        # -------------------
        cache_key = make_key("search_property", {"keyword": keyword})
        cached = cache_get(cache_key)

        if cached:
            return PropertySearchResponse(results=cached)

        # -------------------
        # DB QUERY
        # -------------------
        properties = PropertySearchRepository.search_properties(
            session=session,
            keyword=keyword
        )

        results = [
            PropertyItem.from_orm(p)
            for p in properties
        ]

        # -------------------
        # SAVE CACHE
        # -------------------
        cache_set(cache_key, results, expire_seconds=60 * 10)

        return PropertySearchResponse(results=results)
