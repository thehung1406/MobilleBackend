from pydantic import BaseModel
from typing import List, Optional


class PropertyItem(BaseModel):
    id: int
    name: str
    address: Optional[str]
    image: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]

    class Config:
        from_attributes = True


class PropertySearchRequest(BaseModel):
    keyword: str


class PropertySearchResponse(BaseModel):
    results: List[PropertyItem]
