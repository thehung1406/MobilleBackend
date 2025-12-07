from pydantic import BaseModel, Field
from typing import Optional


class ReviewCreate(BaseModel):
    property_id: int
    rating: int = Field(..., ge=1, le=5)
    description: Optional[str] = None


class ReviewUpdate(BaseModel):
    rating: Optional[int] = Field(None, ge=1, le=5)
    description: Optional[str] = None


class ReviewRead(BaseModel):
    id: int
    user_id: int
    property_id: int
    rating: int
    description: Optional[str]

    class Config:
        from_attributes = True
