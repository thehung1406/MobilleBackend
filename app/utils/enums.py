from enum import Enum


class UserRole(str, Enum):
    SUPER_ADMIN = "super_admin"
    STAFF = "staff"
    CUSTOMER = "customer"


class BookingStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
