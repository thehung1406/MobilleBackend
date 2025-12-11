from typing import Optional
from pydantic import BaseModel


class ReviewBase(BaseModel):
    rating: int
    description: Optional[str] = None


class ReviewCreate(ReviewBase):
    property_id: int


class ReviewRead(ReviewBase):
    id: int
    user_id: int
    user_name: Optional[str] = None

    class Config:
        from_attributes = True
