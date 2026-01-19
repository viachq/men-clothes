"""
HTTP client for communicating with Catalog Service.
"""
from typing import Optional
from fastapi import HTTPException
import httpx

from backend.clients.base_client import BaseServiceClient
from backend.core.config import CATALOG_SERVICE_URL


class CatalogServiceClient(BaseServiceClient):
    """Client for Catalog Service API."""
    
    def __init__(self):
        super().__init__(CATALOG_SERVICE_URL)
    
    def get_product(self, product_id: int) -> dict:
        """
        Get product information by ID.
        
        Args:
            product_id: Product ID
        
        Returns:
            Product data dictionary
        
        Raises:
            HTTPException: If product not found or service unavailable
        """
        try:
            response = self.get(f"/products/{product_id}")
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise HTTPException(status_code=404, detail="Product not found")
            raise
    
    def validate_product_id(self, product_id: int) -> bool:
        """
        Validate that product exists.
        
        Args:
            product_id: Product ID to validate
        
        Returns:
            True if product exists, False otherwise
        """
        try:
            self.get_product(product_id)
            return True
        except HTTPException:
            return False
    
# Singleton instance
_catalog_client: Optional[CatalogServiceClient] = None


def get_catalog_client() -> CatalogServiceClient:
    """Get singleton CatalogServiceClient instance."""
    global _catalog_client
    if _catalog_client is None:
        _catalog_client = CatalogServiceClient()
    return _catalog_client
