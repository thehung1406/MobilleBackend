"""
Import all models to ensure they are registered with SQLModel.

This module imports all SQLModel table classes so that they are
registered with SQLModel's metadata when the application starts.
"""

# Core models
from .user import User
from .organization import Organization, OrganizationMember, OrganizationInvitation

# Property and booking models
from .property import Property
from .room_type import RoomType
from .room import Room
from .rate_plan import RatePlan
from .daily_price import DailyPrice
from .booking import Booking
from .inventory import Inventory

# Property extras
from .property_image import PropertyImage
from .experience import Experience

# Payment and subscription
from .payment import Payment
from .subscription import (
    Subscription, SubscriptionStatus, SubscriptionPlan, 
    BillingCycle, Invoice, InvoiceStatus, InvoiceLineItem
)

# Communication
from .chat_message import ChatMessage
from .email_token import EmailToken
from .customer_profile import (
    PropertyReview, CustomerNotification, ReviewStatus,
    CustomerProfile, CustomerFavorite, BookingPreference, ReviewHelpfulVote
)

__all__ = [
    # Core models
    "User",
    "Organization",
    "OrganizationMember", 
    "OrganizationInvitation",
    
    # Property and booking models
    "Property",
    "RoomType",
    "Room",
    "RatePlan",
    "DailyPrice",
    "Booking",
    "Inventory",
    
    # Property extras
    "PropertyImage",
    "Experience",
    
    # Payment and subscription
    "Payment",
    "Subscription",
    "SubscriptionStatus", 
    "SubscriptionPlan",
    "BillingCycle",
    "Invoice",
    "InvoiceStatus",
    "InvoiceLineItem",
    
    # Communication
    "ChatMessage",
    "EmailToken",
    "PropertyReview",
    "CustomerNotification", 
    "ReviewStatus",
    "CustomerProfile",
    "CustomerFavorite",
    "BookingPreference",
    "ReviewHelpfulVote",
]
