"""
Tests for orders endpoints.
"""
import pytest
from datetime import datetime, timedelta


class TestCreateOrder:
    """Tests for POST /orders endpoint."""
    
    def test_create_order_unauthorized(self, client):
        """Test creating order without authentication."""
        response = client.post(
            "/orders",
            json={"delivery_address": "Test Address"}
        )
        assert response.status_code == 401
    
    def test_create_order_empty_cart(self, client, auth_headers):
        """Test creating order with empty cart."""
        response = client.post(
            "/orders",
            json={"address": "Test Address 123"},
            headers=auth_headers
        )
        assert response.status_code == 400
        assert "empty" in response.json()["detail"].lower()
    
    def test_create_order_with_cart(self, client, auth_headers, test_cart_item):
        """Test creating order from cart."""
        response = client.post(
            "/orders",
            json={"address": "Test Address 123"},
            headers=auth_headers
        )
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["delivery_address"] == "Test Address 123"
        assert "payment_id" in data


class TestListOrders:
    """Tests for GET /orders endpoint."""
    
    def test_list_orders_unauthorized(self, client):
        """Test listing orders without authentication."""
        response = client.get("/orders")
        assert response.status_code == 401
    
    def test_list_orders_empty(self, client, auth_headers):
        """Test listing orders when none exist."""
        response = client.get("/orders", headers=auth_headers)
        assert response.status_code == 200
        assert response.json() == []
    
    def test_list_orders_with_data(self, client, auth_headers, test_order):
        """Test listing orders with data."""
        response = client.get("/orders", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == test_order.id
        assert data[0]["status"] == test_order.status


class TestAdminOrders:
    """Tests for admin order endpoints."""
    
    def test_list_all_orders_unauthorized(self, client):
        """Test listing all orders without authentication."""
        response = client.get("/admin/orders")
        assert response.status_code == 401
    
    def test_list_all_orders_as_client(self, client, auth_headers):
        """Test listing all orders as regular client (should fail)."""
        response = client.get("/admin/orders", headers=auth_headers)
        assert response.status_code == 403
    
    def test_list_all_orders_as_admin(self, client, admin_auth_headers, test_order):
        """Test listing all orders as admin."""
        response = client.get("/admin/orders", headers=admin_auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
    
    def test_get_order_details_as_admin(self, client, admin_auth_headers, test_order):
        """Test getting order details as admin."""
        response = client.get(
            f"/admin/orders/{test_order.id}",
            headers=admin_auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_order.id
