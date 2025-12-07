"""
Schemas for property amenities.

``PropertyAmenityCreate`` captures fields required to create a new
amenity for a property.  ``PropertyAmenityOut`` represents the
amenity returned from the API.
"""

from __future__ import annotations

import uuid
from typing import Optional
from pydantic import BaseModel


class PropertyAmenityCreate(BaseModel):
    property_id: uuid.UUID
    amenity_type: str
    description: Optional[str] = None


class PropertyAmenityOut(BaseModel):
    id: uuid.UUID
    property_id: uuid.UUID
    amenity_type: str
    description: Optional[str]