"""
Enhanced AI Recommendation System for Hotel Booking.

This module provides intelligent recommendations for rooms, properties, and experiences
based on user preferences, booking history, and advanced filtering algorithms.
"""

import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from sqlmodel import Session, select, and_, or_, func
from decimal import Decimal

from app.models.room import Room
from app.models.room_type import RoomType
from app.models.property import Property
from app.models.booking import Booking, BookingStatus
from app.models.user import User
from app.models.experience import Experience
from app.models.daily_price import DailyPrice
from app.models.rate_plan import RatePlan


class AIRecommendationEngine:
    """Advanced AI recommendation engine for hotel bookings."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def recommend_rooms(
        self,
        user_id: Optional[uuid.UUID] = None,
        view: Optional[str] = None,
        price_max: Optional[float] = None,
        capacity: Optional[int] = None,
        check_in: Optional[date] = None,
        check_out: Optional[date] = None,
        city: Optional[str] = None,
        amenities: Optional[List[str]] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get intelligent room recommendations based on user preferences and history.
        
        Args:
            user_id: User ID for personalized recommendations
            view: Preferred view type (ocean, mountain, city, etc.)
            price_max: Maximum price per night
            capacity: Minimum room capacity
            check_in: Check-in date for availability
            check_out: Check-out date for availability
            city: Preferred city
            amenities: List of required amenities
            limit: Maximum number of recommendations
            
        Returns:
            List of recommended rooms with scores and reasons
        """
        # Base query for active rooms
        query = select(Room, RoomType, Property).join(
            RoomType, Room.room_type_id == RoomType.id
        ).join(
            Property, RoomType.property_id == Property.id
        ).where(
            and_(
                Room.is_active == True,
                RoomType.is_active == True,
                Property.is_active == True
            )
        )
        
        # Apply filters
        if view:
            query = query.where(Room.description.ilike(f"%{view}%"))
        
        if price_max:
            query = query.where(Room.price_per_night <= price_max)
        
        if capacity:
            query = query.where(RoomType.max_occupancy >= capacity)
        
        if city:
            query = query.where(Property.city.ilike(f"%{city}%"))
        
        # Check availability if dates provided
        if check_in and check_out:
            # Exclude rooms with conflicting bookings
            conflicting_bookings = select(Booking.room_id).where(
                and_(
                    Booking.status.in_([BookingStatus.CONFIRMED, BookingStatus.PENDING]),
                    or_(
                        and_(Booking.check_in <= check_in, Booking.check_out > check_in),
                        and_(Booking.check_in < check_out, Booking.check_out >= check_out),
                        and_(Booking.check_in >= check_in, Booking.check_out <= check_out)
                    )
                )
            )
            query = query.where(Room.id.notin_(conflicting_bookings))
        
        results = self.session.exec(query).all()
        
        # Score and rank recommendations
        recommendations = []
        user_preferences = self._get_user_preferences(user_id) if user_id else {}
        
        for room, room_type, property in results:
            score = self._calculate_room_score(
                room, room_type, property, user_preferences, 
                view, price_max, capacity, amenities
            )
            
            # Get dynamic pricing if dates provided
            final_price = self._get_dynamic_price(
                room, check_in, check_out
            ) if check_in and check_out else room.price_per_night
            
            recommendations.append({
                "room": {
                    "id": str(room.id),
                    "number": room.number,
                    "description": room.description,
                    "base_price": float(room.price_per_night),
                    "final_price": float(final_price),
                    "capacity": room.capacity,
                    "size_sqm": getattr(room, 'size_sqm', None),
                    "bed_type": getattr(room, 'bed_type', None),
                    "amenities": getattr(room, 'amenities', []),
                },
                "room_type": {
                    "id": str(room_type.id),
                    "name": room_type.name,
                    "description": room_type.description,
                },
                "property": {
                    "id": str(property.id),
                    "name": property.name,
                    "city": property.city,
                    "country": property.country,
                    "rating": float(property.star_rating) if property.star_rating else 0,
                    "address": property.address,
                },
                "score": score,
                "reasons": self._get_recommendation_reasons(
                    room, room_type, property, user_preferences, score
                ),
                "available": True,
                "experiences": self._get_property_experiences(property.id)
            })
        
        # Sort by score and return top recommendations
        recommendations.sort(key=lambda x: x["score"], reverse=True)
        return recommendations[:limit]
    
    def recommend_properties(
        self,
        user_id: Optional[uuid.UUID] = None,
        city: Optional[str] = None,
        price_range: Optional[tuple] = None,
        rating_min: Optional[float] = None,
        amenities: Optional[List[str]] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get property recommendations based on user preferences."""
        query = select(Property).where(Property.is_active == True)
        
        if city:
            query = query.where(Property.city.ilike(f"%{city}%"))
        
        if rating_min:
            query = query.where(Property.rating >= rating_min)
        
        properties = self.session.exec(query).all()
        
        recommendations = []
        user_preferences = self._get_user_preferences(user_id) if user_id else {}
        
        for property in properties:
            # Get price range for this property
            min_price, max_price = self._get_property_price_range(property.id)
            
            # Apply price filter
            if price_range and (max_price < price_range[0] or min_price > price_range[1]):
                continue
            
            score = self._calculate_property_score(property, user_preferences)
            
            recommendations.append({
                "property": {
                    "id": str(property.id),
                    "name": property.name,
                    "description": property.description,
                    "city": property.city,
                    "country": property.country,
                    "rating": float(property.star_rating) if property.star_rating else 0,
                    "address": property.address,
                    "price_range": {"min": float(min_price), "max": float(max_price)},
                    "amenities": property.amenities,
                },
                "score": score,
                "experiences": self._get_property_experiences(property.id),
                "available_room_types": self._get_available_room_types(property.id)
            })
        
        recommendations.sort(key=lambda x: x["score"], reverse=True)
        return recommendations[:limit]
    
    def get_personalized_experiences(
        self,
        user_id: uuid.UUID,
        property_id: Optional[uuid.UUID] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Get personalized experience recommendations."""
        query = select(Experience).where(Experience.is_active == True)
        
        if property_id:
            query = query.where(Experience.property_id == property_id)
        
        experiences = self.session.exec(query).all()
        user_preferences = self._get_user_preferences(user_id)
        
        recommendations = []
        for exp in experiences:
            score = self._calculate_experience_score(exp, user_preferences)
            recommendations.append({
                "experience": {
                    "id": str(exp.id),
                    "name": exp.name,
                    "description": exp.description,
                    "image_url": exp.image_url,
                    "property_id": str(exp.property_id),
                },
                "score": score
            })
        
        recommendations.sort(key=lambda x: x["score"], reverse=True)
        return recommendations[:limit]
    
    def _get_user_preferences(self, user_id: uuid.UUID) -> Dict[str, Any]:
        """Analyze user booking history to extract preferences."""
        # Get user's booking history
        bookings = self.session.exec(
            select(Booking, Room, RoomType, Property)
            .join(Room, Booking.room_id == Room.id)
            .join(RoomType, Room.room_type_id == RoomType.id)
            .join(Property, RoomType.property_id == Property.id)
            .where(
                and_(
                    Booking.user_id == user_id,
                    Booking.status == BookingStatus.COMPLETED
                )
            )
        ).all()
        
        if not bookings:
            return {}
        
        # Analyze preferences
        cities = {}
        price_ranges = []
        amenities = {}
        room_types = {}
        
        for booking, room, room_type, property in bookings:
            # City preferences
            cities[property.city] = cities.get(property.city, 0) + 1
            
            # Price preferences
            price_ranges.append(float(room.price_per_night))
            
            # Amenity preferences
            room_amenities = getattr(room, 'amenities', [])
            if room_amenities:
                for amenity in room_amenities:
                    amenities[amenity] = amenities.get(amenity, 0) + 1
            
            # Room type preferences
            room_types[room_type.name] = room_types.get(room_type.name, 0) + 1
        
        return {
            "preferred_cities": sorted(cities.items(), key=lambda x: x[1], reverse=True),
            "avg_price": sum(price_ranges) / len(price_ranges) if price_ranges else 0,
            "preferred_amenities": sorted(amenities.items(), key=lambda x: x[1], reverse=True),
            "preferred_room_types": sorted(room_types.items(), key=lambda x: x[1], reverse=True),
            "booking_count": len(bookings)
        }
    
    def _calculate_room_score(
        self,
        room: Room,
        room_type: RoomType,
        property: Property,
        user_preferences: Dict[str, Any],
        view: Optional[str],
        price_max: Optional[float],
        capacity: Optional[int],
        amenities: Optional[List[str]]
    ) -> float:
        """Calculate recommendation score for a room."""
        score = 0.0
        
        # Base score from property rating
        if property.star_rating:
            score += float(property.star_rating) * 10
        
        # Price preference matching
        if user_preferences.get("avg_price"):
            price_diff = abs(float(room.price_per_night) - user_preferences["avg_price"])
            price_score = max(0, 50 - (price_diff / user_preferences["avg_price"]) * 50)
            score += price_score
        
        # City preference matching
        preferred_cities = user_preferences.get("preferred_cities", [])
        for city, count in preferred_cities[:3]:  # Top 3 preferred cities
            if property.city.lower() == city.lower():
                score += count * 5
                break
        
        # Amenity matching
        room_amenities = getattr(room, 'amenities', [])
        if amenities and room_amenities:
            matching_amenities = set(amenities) & set(room_amenities)
            score += len(matching_amenities) * 10
        
        # Room type preference
        preferred_room_types = user_preferences.get("preferred_room_types", [])
        for rt_name, count in preferred_room_types[:3]:
            if room_type.name.lower() == rt_name.lower():
                score += count * 3
                break
        
        # View preference
        if view and room.description and view.lower() in room.description.lower():
            score += 15
        
        # Capacity efficiency
        if capacity and room_type.max_occupancy >= capacity:
            # Prefer rooms that match capacity closely
            efficiency = capacity / room_type.max_occupancy
            score += efficiency * 10
        
        return score
    
    def _calculate_property_score(
        self,
        property: Property,
        user_preferences: Dict[str, Any]
    ) -> float:
        """Calculate recommendation score for a property."""
        score = 0.0
        
        # Base score from rating
        if property.star_rating:
            score += float(property.star_rating) * 15
        
        # City preference
        preferred_cities = user_preferences.get("preferred_cities", [])
        for city, count in preferred_cities[:3]:
            if property.city.lower() == city.lower():
                score += count * 8
                break
        
        return score
    
    def _calculate_experience_score(
        self,
        experience: Experience,
        user_preferences: Dict[str, Any]
    ) -> float:
        """Calculate recommendation score for an experience."""
        # Simple scoring based on description keywords
        score = 50.0  # Base score
        
        # Add more sophisticated scoring based on user preferences
        # This could include NLP analysis of descriptions, user reviews, etc.
        
        return score
    
    def _get_dynamic_price(
        self,
        room: Room,
        check_in: date,
        check_out: date
    ) -> Decimal:
        """Get dynamic pricing for a room based on dates."""
        # Check for daily price overrides
        daily_prices = self.session.exec(
            select(DailyPrice).where(
                and_(
                    DailyPrice.room_id == room.id,
                    DailyPrice.date >= check_in,
                    DailyPrice.date < check_out
                )
            )
        ).all()
        
        if daily_prices:
            # Use average of daily prices
            total_price = sum(dp.price for dp in daily_prices)
            return total_price / len(daily_prices)
        
        # Check for rate plan pricing
        rate_plans = self.session.exec(
            select(RatePlan).where(
                and_(
                    RatePlan.room_type_id == room.room_type_id,
                    RatePlan.is_active == True
                )
            )
        ).all()
        
        if rate_plans:
            # Use the best available rate
            return min(rp.base_price for rp in rate_plans)
        
        return room.price_per_night
    
    def _get_property_price_range(self, property_id: uuid.UUID) -> tuple:
        """Get min and max prices for a property."""
        result = self.session.exec(
            select(func.min(Room.price_per_night), func.max(Room.price_per_night))
            .join(RoomType, Room.room_type_id == RoomType.id)
            .where(
                and_(
                    RoomType.property_id == property_id,
                    Room.is_active == True
                )
            )
        ).first()
        
        return result if result and result[0] else (Decimal("0"), Decimal("0"))
    
    def _get_property_experiences(self, property_id: uuid.UUID) -> List[Dict[str, Any]]:
        """Get experiences available at a property."""
        experiences = self.session.exec(
            select(Experience).where(
                and_(
                    Experience.property_id == property_id,
                    Experience.is_active == True
                )
            )
        ).all()
        
        return [
            {
                "id": str(exp.id),
                "name": exp.name,
                "description": exp.description,
                "image_url": exp.image_url
            }
            for exp in experiences
        ]
    
    def _get_available_room_types(self, property_id: uuid.UUID) -> List[Dict[str, Any]]:
        """Get available room types for a property."""
        room_types = self.session.exec(
            select(RoomType).where(
                and_(
                    RoomType.property_id == property_id,
                    RoomType.is_active == True
                )
            )
        ).all()
        
        return [
            {
                "id": str(rt.id),
                "name": rt.name,
                "capacity": rt.capacity,
                "size_sqm": rt.size_sqm,
                "bed_type": rt.bed_type
            }
            for rt in room_types
        ]
    
    def _get_recommendation_reasons(
        self,
        room: Room,
        room_type: RoomType,
        property: Property,
        user_preferences: Dict[str, Any],
        score: float
    ) -> List[str]:
        """Generate human-readable reasons for the recommendation."""
        reasons = []
        
        if property.star_rating and property.star_rating >= 4.0:
            reasons.append(f"Highly rated property ({property.star_rating}/5 stars)")
        
        preferred_cities = user_preferences.get("preferred_cities", [])
        if preferred_cities and any(city[0].lower() == property.city.lower() for city in preferred_cities[:3]):
            reasons.append(f"You've enjoyed staying in {property.city} before")
        
        if user_preferences.get("avg_price"):
            price_diff = abs(float(room.price_per_night) - user_preferences["avg_price"])
            if price_diff / user_preferences["avg_price"] < 0.2:
                reasons.append("Price matches your usual budget")
        
        if score > 80:
            reasons.append("Perfect match for your preferences")
        elif score > 60:
            reasons.append("Great match for your preferences")
        
        return reasons


# Legacy function for backward compatibility
def recommend_rooms(session: Session, view: str | None, price_max: float | None, capacity: int | None):
    """Legacy function - use AIRecommendationEngine for new implementations."""
    engine = AIRecommendationEngine(session)
    recommendations = engine.recommend_rooms(
        view=view,
        price_max=price_max,
        capacity=capacity,
        limit=10
    )
    
    # Convert to old format for compatibility
    return [
        type('Room', (), {
            'id': rec['room']['id'],
            'number': rec['room']['number'],
            'description': rec['room']['description'],
            'price_per_night': rec['room']['base_price'],
            'dict': lambda: rec['room']
        })()
        for rec in recommendations
    ]
