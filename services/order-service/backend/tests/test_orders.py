"""
Tests for orders endpoints.
"""
import pytest
from datetime import datetime, timedelta

from backend.models.promo_code import PromoCode
from backend.models.order import Order
from backend.core.enums import OrderStatus


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


class TestCreateOrderWithPromo:
    """Tests for creating orders with promo codes."""

    def _make_promo(self, test_db, **kwargs):
        defaults = dict(
            code="SAVE10",
            discount_percent=10,
            discount_amount=None,
            min_order_amount=0,
            max_uses=None,
            current_uses=0,
            is_active=True,
            valid_from=None,
            valid_until=None,
        )
        defaults.update(kwargs)
        promo = PromoCode(**defaults)
        test_db.add(promo)
        test_db.commit()
        test_db.refresh(promo)
        return promo

    def test_create_order_with_valid_promo(self, client, auth_headers, test_cart_item, test_db):
        """Order total reduced by discount, promo recorded, current_uses incremented."""
        promo = self._make_promo(test_db, code="SAVE10", discount_percent=10)
        # Cart: quantity 2 * price 1000 = 2000
        response = client.post(
            "/orders",
            json={"address": "Test Address 123", "promo_code": "save10"},
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["promo_code"] == "SAVE10"
        assert data["discount"] == 200  # 10% of 2000
        assert data["total_price"] == 1800

        test_db.refresh(promo)
        assert promo.current_uses == 1

    def test_create_order_with_invalid_promo(self, client, auth_headers, test_cart_item):
        """Invalid promo code returns 400."""
        response = client.post(
            "/orders",
            json={"address": "Test Address 123", "promo_code": "DOESNOTEXIST"},
            headers=auth_headers,
        )
        assert response.status_code == 400


class TestCancelOrder:
    """Tests for PUT /orders/{id}/cancel."""

    def test_owner_cancels_pending_order(self, client, auth_headers, test_order):
        """Owner can cancel a PENDING order."""
        response = client.put(
            f"/orders/{test_order.id}/cancel",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == OrderStatus.CANCELLED.value

    def test_cannot_cancel_non_pending_order(self, client, auth_headers, test_db, test_user):
        """Cannot cancel an order that is not PENDING."""
        order = Order(
            user_id=test_user.id,
            status=OrderStatus.DELIVERED.value,
            delivery_address="Test Address",
            payment_method="card",
            total_price=2000,
        )
        test_db.add(order)
        test_db.commit()
        test_db.refresh(order)

        response = client.put(
            f"/orders/{order.id}/cancel",
            headers=auth_headers,
        )
        assert response.status_code == 400

    def test_cannot_cancel_other_users_order(self, client, auth_headers, test_db):
        """Cannot cancel an order belonging to another user."""
        order = Order(
            user_id=999,
            status=OrderStatus.PENDING.value,
            delivery_address="Other Address",
            payment_method="card",
            total_price=2000,
        )
        test_db.add(order)
        test_db.commit()
        test_db.refresh(order)

        response = client.put(
            f"/orders/{order.id}/cancel",
            headers=auth_headers,
        )
        assert response.status_code == 403

    def test_cancel_missing_order_404(self, client, auth_headers):
        """Cancelling a missing order returns 404."""
        response = client.put(
            "/orders/99999/cancel",
            headers=auth_headers,
        )
        assert response.status_code == 404
