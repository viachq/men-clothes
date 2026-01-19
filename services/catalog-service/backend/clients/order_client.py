"""
HTTP client for communicating with Order Service.
"""
from typing import Optional
from fastapi import HTTPException
import httpx

from backend.clients.base_client import BaseServiceClient
from backend.core.config import ORDER_SERVICE_URL


class OrderServiceClient(BaseServiceClient):
    """Client for Order Service API."""
    
    def __init__(self):
        super().__init__(ORDER_SERVICE_URL)
    
# Singleton instance
_order_client: Optional[OrderServiceClient] = None


def get_order_client() -> OrderServiceClient:
    """Get singleton OrderServiceClient instance."""
    global _order_client
    if _order_client is None:
        _order_client = OrderServiceClient()
    return _order_client
