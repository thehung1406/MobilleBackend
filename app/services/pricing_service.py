"""
Pricing Service for Hotel Booking System.

This service handles all pricing calculations including:
- Base room pricing
- Guest-based pricing
- Seasonal pricing
- Tax calculations
- Discount applications
"""

from datetime import date
from typing import Dict, Any
from decimal import Decimal, ROUND_HALF_UP


class PricingService:
    """Service for calculating room pricing with various factors."""
    
    # Configuration constants
    BASE_GUEST_CAPACITY = 2  # Standard room capacity without extra charges
    EXTRA_GUEST_CHARGE_RATE = 0.15  # 15% of base price per extra guest per night
    TAX_RATE = 0.10  # 10% tax rate
    SERVICE_FEE_RATE = 0.05  # 5% service fee
    
    @staticmethod
    def calculate_room_pricing(
        base_price_per_night: float,
        nights: int,
        guests: int,
        room_capacity: int,
        check_in: date,
        check_out: date
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive room pricing.
        
        Args:
            base_price_per_night: Base price per night for the room
            nights: Number of nights
            guests: Number of guests
            room_capacity: Maximum capacity of the room
            check_in: Check-in date
            check_out: Check-out date
            
        Returns:
            Dictionary with detailed pricing breakdown
        """
        # Validate inputs
        if guests > room_capacity:
            raise ValueError(f"Number of guests ({guests}) exceeds room capacity ({room_capacity})")
        
        if nights <= 0:
            raise ValueError("Number of nights must be positive")
            
        # Convert to Decimal for precise calculations
        base_price = Decimal(str(base_price_per_night))
        
        # Calculate base room cost
        room_total = base_price * nights
        
        # Calculate extra guest charges
        extra_guests = max(0, guests - PricingService.BASE_GUEST_CAPACITY)
        extra_guest_charge_per_night = base_price * Decimal(str(PricingService.EXTRA_GUEST_CHARGE_RATE))
        extra_guest_total = extra_guest_charge_per_night * extra_guests * nights
        
        # Calculate subtotal
        subtotal = room_total + extra_guest_total
        
        # Calculate service fee
        service_fee = subtotal * Decimal(str(PricingService.SERVICE_FEE_RATE))
        
        # Calculate taxes (on subtotal + service fee)
        taxable_amount = subtotal + service_fee
        taxes = taxable_amount * Decimal(str(PricingService.TAX_RATE))
        
        # Calculate final total
        total_price = subtotal + service_fee + taxes
        
        # Round all amounts to 2 decimal places
        def round_decimal(amount: Decimal) -> float:
            return float(amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
        
        return {
            "base_price_per_night": round_decimal(base_price),
            "nights": nights,
            "guests": guests,
            "room_capacity": room_capacity,
            "room_total": round_decimal(room_total),
            "extra_guests": extra_guests,
            "extra_guest_charge_per_night": round_decimal(extra_guest_charge_per_night),
            "extra_guest_total": round_decimal(extra_guest_total),
            "subtotal": round_decimal(subtotal),
            "service_fee_rate": PricingService.SERVICE_FEE_RATE,
            "service_fee": round_decimal(service_fee),
            "tax_rate": PricingService.TAX_RATE,
            "taxes": round_decimal(taxes),
            "total_price": round_decimal(total_price),
            "breakdown_summary": {
                "room_cost": f"${round_decimal(base_price)} × {nights} nights = ${round_decimal(room_total)}",
                "extra_guest_cost": f"{extra_guests} extra guests × ${round_decimal(extra_guest_charge_per_night)} × {nights} nights = ${round_decimal(extra_guest_total)}" if extra_guests > 0 else "No extra guests",
                "service_fee_desc": f"Service fee ({PricingService.SERVICE_FEE_RATE*100}%) = ${round_decimal(service_fee)}",
                "tax_desc": f"Taxes ({PricingService.TAX_RATE*100}%) = ${round_decimal(taxes)}",
                "total_desc": f"Total = ${round_decimal(total_price)}"
            }
        }
    
    @staticmethod
    def apply_seasonal_pricing(
        base_pricing: Dict[str, Any],
        check_in: date,
        check_out: date
    ) -> Dict[str, Any]:
        """
        Apply seasonal pricing adjustments.
        
        Args:
            base_pricing: Base pricing calculation result
            check_in: Check-in date
            check_out: Check-out date
            
        Returns:
            Updated pricing with seasonal adjustments
        """
        # Determine if dates fall in peak season
        is_peak_season = PricingService._is_peak_season(check_in, check_out)
        
        if is_peak_season:
            # Apply 20% peak season surcharge
            peak_multiplier = Decimal('1.20')
            original_total = Decimal(str(base_pricing['total_price']))
            peak_surcharge = original_total * (peak_multiplier - 1)
            new_total = original_total + peak_surcharge
            
            base_pricing.update({
                'is_peak_season': True,
                'peak_season_surcharge': float(peak_surcharge.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                'total_price': float(new_total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                'original_total': float(original_total)
            })
        else:
            base_pricing.update({
                'is_peak_season': False,
                'peak_season_surcharge': 0.0
            })
            
        return base_pricing
    
    @staticmethod
    def _is_peak_season(check_in: date, check_out: date) -> bool:
        """
        Determine if the booking dates fall in peak season.
        
        Peak seasons:
        - December 20 - January 5 (Holiday season)
        - July 1 - August 31 (Summer season)
        """
        # Holiday season (Dec 20 - Jan 5)
        for single_date in PricingService._date_range(check_in, check_out):
            if (single_date.month == 12 and single_date.day >= 20) or \
               (single_date.month == 1 and single_date.day <= 5) or \
               (single_date.month in [7, 8]):  # Summer season
                return True
        return False
    
    @staticmethod
    def _date_range(start_date: date, end_date: date):
        """Generate date range between start and end dates."""
        current_date = start_date
        while current_date < end_date:
            yield current_date
            current_date = date.fromordinal(current_date.toordinal() + 1)
