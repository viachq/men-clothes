"""
Application-wide enumerations for type safety and validation.
"""
import enum


class UserRole(enum.Enum):
    """User role types."""
    CLIENT = "client"
    MANAGER = "manager"
    SYSTEM_ADMIN = "system_admin"


class OrderStatus(enum.Enum):
    """Order status lifecycle."""
    PENDING = "pending"
    DELIVERING = "delivering"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class PaymentStatus(enum.Enum):
    """Payment status types."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class PaymentMethod(enum.Enum):
    """Payment method types."""
    CARD = "card"
    CASH = "cash"
    ONLINE = "online"

