"""
Schema definitions for Room resources, including creation and update models.

This module extends the original Room schemas to support partial updates.  The
``RoomCreate`` model defines the required fields when creating a new room.
The ``RoomOut`` model represents the object returned from the API.  To allow
clients to modify existing rooms without providing every field, the
``RoomUpdate`` model exposes all mutable fields as optional so that only
provided values are updated.  Consumers should omit fields they do not wish
to modify.
"""

from __future__ import annotations

from typing import Optional
import uuid
from pydantic import BaseModel


class RoomCreate(BaseModel):
    """Schema used when creating a new room."""

    number: str
    type: str = "standard"
    price_per_night: float
    capacity: int = 2
    description: Optional[str] = None
    image_url: Optional[str] = None
    # optional reference to the room type.  When provided, the new room will
    # be associated with a RoomType, allowing richer categorisation and pricing.
    room_type_id: Optional[uuid.UUID] = None
    # Optional property reference; when creating a room you can specify
    # either ``property_id`` or derive it through the chosen room type.
    property_id: Optional[uuid.UUID] = None


class RoomUpdate(BaseModel):
    """Schema used for partial updates to a room.

    All fields are optional.  Fields left unset (``None``) will not be
    updated on the target resource.  This model allows the API to support
    PATCH semantics where clients can send only the fields they want to
    change.
    """

    number: Optional[str] = None
    type: Optional[str] = None
    price_per_night: Optional[float] = None
    capacity: Optional[int] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    is_active: Optional[bool] = None
    room_type_id: Optional[uuid.UUID] = None
    property_id: Optional[uuid.UUID] = None


class RoomOut(BaseModel):
    """Schema returned from the API for a room resource."""

    id: uuid.UUID
    number: str
    type: str
    price_per_night: float
    capacity: int
    description: Optional[str] = None
    image_url: Optional[str] = None
    is_active: bool
    # include the room_type_id in the API response to help clients resolve
    # category information.  The ``type`` field remains for backward
    # compatibility but should gradually be replaced by using ``room_type_id``.
    room_type_id: Optional[uuid.UUID] = None
    property_id: Optional[uuid.UUID] = None