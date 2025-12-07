"""
Schema definitions for Booking resources.

This module defines Pydantic models used for creating, updating and
representing bookings in the API.  The ``BookingCreate`` model captures
fields required to create a booking.  ``BookingUpdate`` exposes optional
fields for modifying an existing booking, including changing the check-in
and check-out dates or updating the booking status.  ``BookingOut`` is
returned from the API and includes immutable identifiers and calculated
amounts.
"""

from __future__ import annotations

from typing import Optional
from datetime import date
import uuid
from pydantic import BaseModel


class BookingCreate(BaseModel):
    """Schema used to create a new booking."""

    room_id: uuid.UUID
    check_in: date
    check_out: date
    # Optional references used for category and pricing lookups.  When
    # provided, ``property_id`` and ``room_type_id`` should match the
    # associated room.  ``rate_plan_id`` identifies the pricing plan to
    # calculate the total cost.
    property_id: Optional[uuid.UUID] = None
    room_type_id: Optional[uuid.UUID] = None
    rate_plan_id: Optional[uuid.UUID] = None


class BookingUpdate(BaseModel):
    """Schema used for partial updates to a booking.

    Clients may update the check-in and check-out dates to modify their
    reservation or adjust the booking status (e.g. to cancel a booking).  All
    fields are optional; only provided values will be applied.
    """

    check_in: Optional[date] = None
    check_out: Optional[date] = None
    status: Optional[str] = None
    property_id: Optional[uuid.UUID] = None
    room_type_id: Optional[uuid.UUID] = None
    rate_plan_id: Optional[uuid.UUID] = None


class BookingOut(BaseModel):
    """Schema returned from the API for a booking resource."""

    id: uuid.UUID
    user_id: uuid.UUID
    room_id: uuid.UUID
    check_in: date
    check_out: date
    total_amount: float
    status: str
    # Include relational identifiers to assist the client in navigating the
    # booking's context (property, room type and rate plan).  These fields
    # are optional to ensure backwards compatibility with older bookings.
    property_id: Optional[uuid.UUID] = None
    room_type_id: Optional[uuid.UUID] = None
    rate_plan_id: Optional[uuid.UUID] = None