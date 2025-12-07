"""
Enhanced booking service for SAAS hotel booking system.

This service handles booking operations with multi-tenancy support,
advanced pricing, inventory management, and business rules.
"""

from __future__ import annotations

import uuid
from datetime import date, datetime, timedelta
from typing import List, Optional, Dict, Any
from decimal import Decimal
from enum import Enum

from sqlmodel import Session, select, and_, or_, func
from fastapi import HTTPException

from app.models.booking import Booking, BookingStatus
from app.models.room import Room
from app.models.room_type import RoomType
from app.models.rate_plan import RatePlan
from app.models.daily_price import DailyPrice
from app.models.inventory import Inventory
from app.models.property import Property
from app.models.user import User
from app.models.organization import Organization
from app.utils.helpers import nights_between


class BookingService:
    """Enhanced booking service with SAAS features."""

    def __init__(self, session: Session):
        self.session = session
    
    def create_booking(
        self,
        user_id: uuid.UUID,
        room_type_id: uuid.UUID,
        rate_plan_id: uuid.UUID,
        check_in: date,
        check_out: date,
        guests: int = 2,
        special_requests: Optional[str] = None,
        organization_id: Optional[uuid.UUID] = None
    ) -> Booking:
        """
        Create a new booking with enhanced validation and pricing.
        
        This method handles the complete booking flow including:
        - Availability validation
        - Pricing calculation
        - Inventory management
        - Multi-tenant validation
        """
        
        # Validate dates
        if check_in >= check_out:
            raise HTTPException(
                status_code=400,
                detail="Check-in date must be before check-out date"
            )
        
        if check_in < date.today():
            raise HTTPException(
                status_code=400,
                detail="Check-in date cannot be in the past"
            )
        
        # Get room type and validate
        room_type = self.session.get(RoomType, room_type_id)
        if not room_type or not room_type.is_active:
            raise HTTPException(status_code=404, detail="Room type not found")
        
        # Validate guest count
        if guests > room_type.max_occupancy:
            raise HTTPException(
                status_code=400,
                detail=f"Room type can accommodate maximum {room_type.max_occupancy} guests"
            )
        
        # Get property and validate organization access
        property = self.session.get(Property, room_type.property_id)
        if not property or not property.is_active:
            raise HTTPException(status_code=404, detail="Property not found")
        
        # Multi-tenant validation
        if organization_id and property.organization_id != organization_id:
            raise HTTPException(
                status_code=403,
                detail="Property does not belong to your organization"
            )
        
        # Get and validate rate plan
        rate_plan = self.session.get(RatePlan, rate_plan_id)
        if not rate_plan or rate_plan.room_type_id != room_type_id:
            raise HTTPException(status_code=404, detail="Rate plan not found")
        
        # Check availability
        if not self.check_room_type_availability(room_type_id, check_in, check_out):
            raise HTTPException(
                status_code=400,
                detail="No rooms available for the selected dates"
            )
        
        # Calculate pricing
        pricing = self.calculate_booking_price(rate_plan_id, check_in, check_out)
        
        # Find and assign a specific room
        available_room = self.find_available_room(room_type_id, check_in, check_out)
        if not available_room:
            raise HTTPException(
                status_code=400,
                detail="No specific room available for assignment"
            )
        
        # Create booking
        booking = Booking(
            user_id=user_id,
            room_id=available_room.id,
            room_type_id=room_type_id,
            rate_plan_id=rate_plan_id,
            property_id=property.id,
            check_in=check_in,
            check_out=check_out,
            total_amount=pricing["total_price"],
            status=BookingStatus.PENDING,
            # Add additional fields for enhanced booking
            guest_count=guests,
            special_requests=special_requests
        )
        
        self.session.add(booking)
        self.session.commit()
        self.session.refresh(booking)
        
        # Update inventory if managed
        self.update_inventory_on_booking(room_type_id, check_in, check_out, -1)
        
        return booking
    
    def check_room_type_availability(
        self,
        room_type_id: uuid.UUID,
        check_in: date,
        check_out: date
    ) -> bool:
        """Check if room type has availability for date range."""
        
        # Get total rooms of this type
        total_rooms = self.session.exec(
            select(func.count(Room.id)).where(
                and_(
                    Room.room_type_id == room_type_id,
                    Room.is_active == True
                )
            )
        ).first() or 0
        
        if total_rooms == 0:
            return False
        
        # Get booked rooms for the date range
        booked_count = self.session.exec(
            select(func.count(Booking.id)).where(
                and_(
                    Booking.room_type_id == room_type_id,
                    Booking.status.in_([BookingStatus.CONFIRMED, BookingStatus.PENDING]),
                    or_(
                        and_(Booking.check_in <= check_in, Booking.check_out > check_in),
                        and_(Booking.check_in < check_out, Booking.check_out >= check_out),
                        and_(Booking.check_in >= check_in, Booking.check_out <= check_out)
                    )
                )
            )
        ).first() or 0
        
        # Check inventory restrictions
        inventory_available = self.check_inventory_availability(
            room_type_id, check_in, check_out
        )
        
        available_rooms = min(total_rooms - booked_count, inventory_available)
        return available_rooms > 0
    
    def find_available_room(
        self,
        room_type_id: uuid.UUID,
        check_in: date,
        check_out: date
    ) -> Optional[Room]:
        """Find a specific room that's available for the date range."""
        
        # Get all rooms of this type
        rooms = self.session.exec(
            select(Room).where(
                and_(
                    Room.room_type_id == room_type_id,
                    Room.is_active == True
                )
            )
        ).all()
        
        # Check each room for availability
        for room in rooms:
            if self.room_available(room.id, check_in, check_out):
                return room
        
        return None
    
    def room_available(self, room_id: uuid.UUID, check_in: date, check_out: date) -> bool:
        """
        Check if a specific room is available for the given date range.
        
        Enhanced version with better overlap detection and status checking.
        """
        overlapping_bookings = self.session.exec(
            select(Booking).where(
                and_(
        Booking.room_id == room_id,
                    Booking.status.in_([BookingStatus.CONFIRMED, BookingStatus.PENDING]),
                    or_(
                        and_(Booking.check_in <= check_in, Booking.check_out > check_in),
                        and_(Booking.check_in < check_out, Booking.check_out >= check_out),
                        and_(Booking.check_in >= check_in, Booking.check_out <= check_out)
                    )
                )
            )
        ).first()
        
        return overlapping_bookings is None
    
    def calculate_booking_price(
        self,
        rate_plan_id: uuid.UUID,
        check_in: date,
        check_out: date
    ) -> Dict[str, Any]:
        """Calculate total price for a booking with daily price support."""
        
        rate_plan = self.session.get(RatePlan, rate_plan_id)
        if not rate_plan:
            raise HTTPException(status_code=404, detail="Rate plan not found")
        
        nights = (check_out - check_in).days
        if nights <= 0:
            raise HTTPException(status_code=400, detail="Invalid date range")
        
        # Get daily prices if available
        daily_prices = self.session.exec(
            select(DailyPrice).where(
                and_(
                    DailyPrice.rate_plan_id == rate_plan_id,
                    DailyPrice.date >= check_in,
                    DailyPrice.date < check_out
                )
            )
        ).all()
        
        # Create a map of date -> price
        daily_price_map = {dp.date: dp.price for dp in daily_prices}
        
        # Calculate total price
        total_price = 0.0
        current_date = check_in
        daily_breakdown = []
        
        while current_date < check_out:
            if current_date in daily_price_map:
                day_price = float(daily_price_map[current_date])
            else:
                day_price = float(rate_plan.base_price)
            
            total_price += day_price
            daily_breakdown.append({
                "date": current_date,
                "price": day_price
            })
            
            current_date += timedelta(days=1)
        
        return {
            "total_price": total_price,
            "nights": nights,
            "avg_price_per_night": total_price / nights,
            "currency": rate_plan.currency,
            "daily_breakdown": daily_breakdown,
            "rate_plan": {
                "id": rate_plan.id,
                "name": rate_plan.name,
                "is_refundable": rate_plan.is_refundable,
                "cancellation_policy": rate_plan.cancellation_policy
            }
        }
    
    def check_inventory_availability(
        self,
        room_type_id: uuid.UUID,
        check_in: date,
        check_out: date
    ) -> int:
        """Check inventory-based availability restrictions."""
        
        inventory_records = self.session.exec(
            select(Inventory).where(
                and_(
                    Inventory.room_type_id == room_type_id,
                    Inventory.date >= check_in,
                    Inventory.date < check_out
                )
            )
        ).all()
        
        if not inventory_records:
            # No inventory restrictions
            return 999
        
        # Return minimum available across all dates
        return min(record.available_rooms for record in inventory_records)
    
    def update_inventory_on_booking(
        self,
        room_type_id: uuid.UUID,
        check_in: date,
        check_out: date,
        quantity_change: int
    ):
        """Update inventory when booking is created or cancelled."""
        
        current_date = check_in
        while current_date < check_out:
            inventory = self.session.exec(
                select(Inventory).where(
                    and_(
                        Inventory.room_type_id == room_type_id,
                        Inventory.date == current_date
                    )
                )
            ).first()
            
            if inventory:
                inventory.available_rooms += quantity_change
                # Ensure we don't go below 0
                inventory.available_rooms = max(0, inventory.available_rooms)
                self.session.add(inventory)
            
            current_date += timedelta(days=1)
        
        self.session.commit()
    
    def cancel_booking(
        self,
        booking_id: uuid.UUID,
        user_id: Optional[uuid.UUID] = None,
        reason: Optional[str] = None
    ) -> Booking:
        """Cancel a booking with inventory restoration."""
        
        booking = self.session.get(Booking, booking_id)
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        
        # Check authorization
        if user_id and booking.user_id != user_id:
            raise HTTPException(
                status_code=403,
                detail="Not authorized to cancel this booking"
            )
        
        # Check if booking can be cancelled
        if booking.status in [BookingStatus.CANCELLED, BookingStatus.COMPLETED]:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot cancel booking with status: {booking.status}"
            )
        
        # Update booking status
        booking.status = BookingStatus.CANCELLED
        booking.updated_at = datetime.utcnow()
        # Add cancellation reason if provided
        if reason:
            booking.cancellation_reason = reason
        
        self.session.add(booking)
        
        # Restore inventory
        if booking.room_type_id:
            self.update_inventory_on_booking(
                booking.room_type_id,
                booking.check_in,
                booking.check_out,
                1  # Add back the room
            )
        
        self.session.commit()
        self.session.refresh(booking)
        
        return booking
    
    def confirm_booking(self, booking_id: uuid.UUID) -> Booking:
        """Confirm a pending booking."""
        
        booking = self.session.get(Booking, booking_id)
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        
        if booking.status != BookingStatus.PENDING:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot confirm booking with status: {booking.status}"
            )
        
        booking.status = BookingStatus.CONFIRMED
        booking.updated_at = datetime.utcnow()
        
        self.session.add(booking)
        self.session.commit()
        self.session.refresh(booking)
        
        return booking
    
    def get_organization_bookings(
        self,
        organization_id: uuid.UUID,
        status_filter: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Booking]:
        """Get bookings for an organization's properties."""
        
        # Get property IDs for this organization
        property_ids = self.session.exec(
            select(Property.id).where(Property.organization_id == organization_id)
        ).all()
        
        if not property_ids:
            return []
        
        # Build query for bookings
        query = select(Booking).where(Booking.property_id.in_(property_ids))
        
        if status_filter:
            query = query.where(Booking.status == status_filter)
        
        query = query.order_by(Booking.created_at.desc()).offset(offset).limit(limit)
        
        return self.session.exec(query).all()


# Legacy functions for backward compatibility
def room_available(session: Session, room_id, check_in: date, check_out: date) -> bool:
    """Legacy function - use BookingService.room_available instead."""
    service = BookingService(session)
    return service.room_available(room_id, check_in, check_out)


def compute_total(room: Room, check_in: date, check_out: date) -> float:
    """Legacy function - use BookingService.calculate_booking_price instead."""
    nights = nights_between(check_in, check_out)
    if nights <= 0:
        raise ValueError("Invalid dates")
    return nights * room.price_per_night
