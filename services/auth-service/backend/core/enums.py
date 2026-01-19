"""
Application-wide enumerations for type safety and validation.
"""
import enum


class UserRole(enum.Enum):
    """User role types."""
    CLIENT = "client"
    MANAGER = "manager"
    SYSTEM_ADMIN = "system_admin"

