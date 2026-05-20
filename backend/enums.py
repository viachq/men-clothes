import enum


class UserRole(enum.Enum):
    CLIENT = "client"
    MANAGER = "manager"
    SYSTEM_ADMIN = "system_admin"


class OrderStatus(enum.Enum):
    PENDING = "pending"
    DELIVERING = "delivering"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class PaymentStatus(enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class PaymentMethod(enum.Enum):
    CARD = "card"
    CASH = "cash"
    ONLINE = "online"
