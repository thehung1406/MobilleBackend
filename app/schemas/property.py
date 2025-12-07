"""
Pydantic schemas for Property resources.

``PropertyCreate`` defines the data required to create a new property.
``PropertyOut`` represents a property when returned from the API.
"""

from __future__ import annotations

import uuid
from typing import Optional
from pydantic import BaseModel


class PropertyCreate(BaseModel):
    name: str
    location: Optional[str] = None
    description: Optional[str] = None


class PropertyOut(BaseModel):
    id: uuid.UUID
    name: str
    location: Optional[str]
    description: Optional[str]
    is_active: bool