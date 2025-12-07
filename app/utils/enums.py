from enum import Enum

class UserRole(str, Enum):
    super_admin = "super_admin"
    staff = "staff"
    customer = "customer"
