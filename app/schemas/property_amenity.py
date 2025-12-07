from pydantic import BaseModel

class PropertyAmenityCreate(BaseModel):
    property_id: int
    amenity_id: int


class PropertyAmenityRead(BaseModel):
    id: int
    property_id: int
    amenity_id: int

    class Config:
        from_attributes = True
