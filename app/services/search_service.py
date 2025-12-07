"""
Search and availability service for hotel booking system.

This service handles property search, room availability checks,
and pricing calculations for the SAAS hotel booking platform.
"""

from __future__ import annotations

import uuid
from datetime import date, datetime, timedelta
from typing import List, Optional, Dict, Any
from decimal import Decimal

from sqlmodel import Session, select, and_, or_, func
from fastapi import HTTPException

from app.models.property import Property
from app.models.room_type import RoomType
from app.models.room import Room
from app.models.rate_plan import RatePlan
from app.models.daily_price import DailyPrice
from app.models.booking import Booking, BookingStatus
from app.models.inventory import Inventory
from app.models.organization import Organization


class SearchService:
    """Service for handling property search and availability."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def search_properties(
        self,
        city: Optional[str] = None,
        check_in: Optional[date] = None,
        check_out: Optional[date] = None,
        guests: int = 2,
        property_type: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        organization_id: Optional[uuid.UUID] = None,
        limit: int = 20,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Search for available properties based on criteria.
        
        Returns properties with available room types and pricing.
        """
        # Base query for properties
        query = select(Property).where(Property.is_active == True)
        
        # Filter by organization (multi-tenancy)
        if organization_id:
            query = query.where(Property.organization_id == organization_id)
        
        # Filter by city
        if city:
            query = query.where(Property.city.ilike(f"%{city}%"))
        
        # Filter by property type
        if property_type:
            query = query.where(Property.property_type == property_type)
        
        # Get properties
        properties = self.session.exec(query.offset(offset).limit(limit)).all()
        
        results = []
        for property in properties:
            # Get available room types for this property
            available_rooms = self.get_available_room_types(
                property_id=property.id,
                check_in=check_in,
                check_out=check_out,
                guests=guests,
                min_price=min_price,
                max_price=max_price
            )
            
            if available_rooms:  # Only include properties with available rooms
                property_data = {
                    "id": property.id,
                    "name": property.name,
                    "location": property.location,
                    "city": property.city,
                    "country": property.country,
                    "property_type": property.property_type,
                    "star_rating": property.star_rating,
                    "main_image_url": property.main_image_url,
                    "description": property.description,
                    "available_room_types": available_rooms,
                    "min_price": min(room["price"] for room in available_rooms),
                    "currency": property.currency
                }
                results.append(property_data)
        
        # Get total count for pagination
        total_query = select(func.count(Property.id)).where(
            Property.is_active == True
        )
        if organization_id:
            total_query = total_query.where(Property.organization_id == organization_id)
        if city:
            total_query = total_query.where(Property.city.ilike(f"%{city}%"))
        if property_type:
            total_query = total_query.where(Property.property_type == property_type)
        
        total = self.session.exec(total_query).first()
        
        return {
            "properties": results,
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_more": offset + limit < total
        }
    
    def get_available_room_types(
        self,
        property_id: uuid.UUID,
        check_in: Optional[date] = None,
        check_out: Optional[date] = None,
        guests: int = 2,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """Get available room types for a property with pricing."""
        
        # Get room types for this property
        room_types = self.session.exec(
            select(RoomType).where(
                and_(
                    RoomType.property_id == property_id,
                    RoomType.is_active == True,
                    RoomType.max_occupancy >= guests
                )
            )
        ).all()
        
        available_room_types = []
        
        for room_type in room_types:
            # Check availability if dates provided
            if check_in and check_out:
                available_count = self.get_room_type_availability(
                    room_type.id, check_in, check_out
                )
                if available_count <= 0:
                    continue
            else:
                available_count = self.get_total_rooms_for_type(room_type.id)
            
            # Get pricing
            pricing = self.calculate_room_type_pricing(
                room_type.id, check_in, check_out
            )
            
            # Apply price filters
            if min_price and pricing["total_price"] < min_price:
                continue
            if max_price and pricing["total_price"] > max_price:
                continue
            
            room_type_data = {
                "id": room_type.id,
                "name": room_type.name,
                "description": room_type.description,
                "max_occupancy": room_type.max_occupancy,
                "available_count": available_count,
                "price": pricing["total_price"],
                "price_per_night": pricing["avg_price_per_night"],
                "currency": pricing["currency"],
                "nights": pricing["nights"],
                "rate_plans": pricing["rate_plans"]
            }
            available_room_types.append(room_type_data)
        
        return available_room_types
    
    def get_room_type_availability(
        self,
        room_type_id: uuid.UUID,
        check_in: date,
        check_out: date
    ) -> int:
        """Check how many rooms of this type are available for the date range."""
        
        # Get total rooms of this type
        total_rooms = self.get_total_rooms_for_type(room_type_id)
        
        # Get booked rooms for the date range
        booked_rooms = self.session.exec(
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
        
        # Check inventory restrictions if any
        inventory_available = self.check_inventory_availability(
            room_type_id, check_in, check_out
        )
        
        return min(total_rooms - booked_rooms, inventory_available)
    
    def get_total_rooms_for_type(self, room_type_id: uuid.UUID) -> int:
        """Get total number of rooms for a room type."""
        return self.session.exec(
            select(func.count(Room.id)).where(
                and_(
                    Room.room_type_id == room_type_id,
                    Room.is_active == True
                )
            )
        ).first() or 0
    
    def check_inventory_availability(
        self,
        room_type_id: uuid.UUID,
        check_in: date,
        check_out: date
    ) -> int:
        """Check inventory-based availability restrictions."""
        
        # Get inventory records for the date range
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
            # No inventory restrictions, return large number
            return 999
        
        # Return minimum available across all dates
        return min(record.available_rooms for record in inventory_records)
    
    def calculate_room_type_pricing(
        self,
        room_type_id: uuid.UUID,
        check_in: Optional[date] = None,
        check_out: Optional[date] = None
    ) -> Dict[str, Any]:
        """Calculate pricing for a room type over a date range."""
        
        # Get rate plans for this room type
        rate_plans = self.session.exec(
            select(RatePlan).where(RatePlan.room_type_id == room_type_id)
        ).all()
        
        if not rate_plans:
            return {
                "total_price": 0.0,
                "avg_price_per_night": 0.0,
                "currency": "USD",
                "nights": 0,
                "rate_plans": []
            }
        
        # Use the first rate plan as default (could be enhanced to select best rate)
        default_rate_plan = rate_plans[0]
        
        if not check_in or not check_out:
            return {
                "total_price": float(default_rate_plan.base_price),
                "avg_price_per_night": float(default_rate_plan.base_price),
                "currency": default_rate_plan.currency,
                "nights": 1,
                "rate_plans": [self._format_rate_plan(default_rate_plan)]
            }
        
        # Calculate nights
        nights = (check_out - check_in).days
        if nights <= 0:
            raise HTTPException(status_code=400, detail="Invalid date range")
        
        # Get daily prices if available
        daily_prices = self.session.exec(
            select(DailyPrice).where(
                and_(
                    DailyPrice.rate_plan_id == default_rate_plan.id,
                    DailyPrice.date >= check_in,
                    DailyPrice.date < check_out
                )
            )
        ).all()
        
        # Calculate total price
        total_price = 0.0
        current_date = check_in
        
        while current_date < check_out:
            # Check if there's a daily price for this date
            daily_price = next(
                (dp for dp in daily_prices if dp.date == current_date),
                None
            )
            
            if daily_price:
                total_price += float(daily_price.price)
            else:
                total_price += float(default_rate_plan.base_price)
            
            current_date += timedelta(days=1)
        
        avg_price_per_night = total_price / nights
        
        return {
            "total_price": total_price,
            "avg_price_per_night": avg_price_per_night,
            "currency": default_rate_plan.currency,
            "nights": nights,
            "rate_plans": [self._format_rate_plan(rp) for rp in rate_plans]
        }
    
    def _format_rate_plan(self, rate_plan: RatePlan) -> Dict[str, Any]:
        """Format rate plan for API response."""
        return {
            "id": rate_plan.id,
            "name": rate_plan.name,
            "base_price": float(rate_plan.base_price),
            "currency": rate_plan.currency,
            "is_refundable": rate_plan.is_refundable,
            "cancellation_policy": rate_plan.cancellation_policy
        }
    
    def get_property_details(
        self,
        property_id: uuid.UUID,
        check_in: Optional[date] = None,
        check_out: Optional[date] = None,
        guests: int = 2
    ) -> Dict[str, Any]:
        """Get detailed property information with availability and pricing."""
        
        property = self.session.get(Property, property_id)
        if not property or not property.is_active:
            raise HTTPException(status_code=404, detail="Property not found")
        
        # Get organization info
        organization = self.session.get(Organization, property.organization_id)
        
        # Get available room types
        available_rooms = self.get_available_room_types(
            property_id=property_id,
            check_in=check_in,
            check_out=check_out,
            guests=guests
        )
        
        # Get property amenities, images, etc. (would need to implement these models)
        
        return {
            "id": property.id,
            "name": property.name,
            "description": property.description,
            "property_type": property.property_type,
            "star_rating": property.star_rating,
            "address": property.address,
            "city": property.city,
            "country": property.country,
            "postal_code": property.postal_code,
            "latitude": property.latitude,
            "longitude": property.longitude,
            "contact_email": property.contact_email,
            "contact_phone": property.contact_phone,
            "check_in_time": property.check_in_time,
            "check_out_time": property.check_out_time,
            "currency": property.currency,
            "cancellation_policy": property.cancellation_policy,
            "house_rules": property.house_rules,
            "main_image_url": property.main_image_url,
            "organization": {
                "id": organization.id,
                "name": organization.name,
                "slug": organization.slug
            } if organization else None,
            "available_room_types": available_rooms,
            "min_price": min(room["price"] for room in available_rooms) if available_rooms else None
        }
