from fastapi import HTTPException
from sqlmodel import Session

from app.repositories.property_search_repo import PropertySearchRepository


class PropertySearchService:

    def __init__(self):
        self.repo = PropertySearchRepository()

    def search_properties(self, session: Session, keyword: str):

        # -----------------------------------------
        # 1. Normalize keyword
        # -----------------------------------------
        if not keyword or not keyword.strip():
            raise HTTPException(400, "Keyword must not be empty")

        keyword = keyword.strip().lower()

        # -----------------------------------------
        # 2. Query DB
        # -----------------------------------------
        results = self.repo.search(session, keyword)

        # -----------------------------------------
        # 3. If no results
        # -----------------------------------------
        if not results:
            return []  # FE sẽ show "Không tìm thấy khách sạn"

        # -----------------------------------------
        # 4. Return result list
        # -----------------------------------------
        return results
