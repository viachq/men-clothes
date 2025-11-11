"""
Services module for business logic.
"""
from backend.services.telegram_notifier import send_new_order_notification

__all__ = ["send_new_order_notification"]

