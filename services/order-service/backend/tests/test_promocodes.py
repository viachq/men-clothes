"""
Tests for promo code endpoints.
"""
import pytest
from datetime import datetime, timedelta

from backend.models.promo_code import PromoCode


def _make_promo(test_db, **kwargs):
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


class TestValidatePromo:
    """Tests for POST /promo/validate."""

    def test_valid_percent_code(self, client, test_db):
        _make_promo(test_db, code="SAVE10", discount_percent=10)
        response = client.post(
            "/promo/validate",
            json={"code": "SAVE10", "order_total": 1000},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True
        assert data["discount"] == 100  # 10% of 1000

    def test_nonexistent_code(self, client):
        response = client.post(
            "/promo/validate",
            json={"code": "NOPE", "order_total": 1000},
        )
        assert response.status_code == 200
        assert response.json()["valid"] is False

    def test_inactive_code(self, client, test_db):
        _make_promo(test_db, code="OFF", discount_percent=10, is_active=False)
        response = client.post(
            "/promo/validate",
            json={"code": "OFF", "order_total": 1000},
        )
        assert response.status_code == 200
        assert response.json()["valid"] is False

    def test_min_order_not_met(self, client, test_db):
        _make_promo(test_db, code="BIG", discount_percent=10, min_order_amount=5000)
        response = client.post(
            "/promo/validate",
            json={"code": "BIG", "order_total": 1000},
        )
        assert response.status_code == 200
        assert response.json()["valid"] is False

    def test_expired_code(self, client, test_db):
        _make_promo(
            test_db,
            code="OLD",
            discount_percent=10,
            valid_until=datetime.utcnow() - timedelta(days=1),
        )
        response = client.post(
            "/promo/validate",
            json={"code": "OLD", "order_total": 1000},
        )
        assert response.status_code == 200
        assert response.json()["valid"] is False

    def test_max_uses_exhausted(self, client, test_db):
        _make_promo(
            test_db,
            code="LIMITED",
            discount_percent=10,
            max_uses=2,
            current_uses=2,
        )
        response = client.post(
            "/promo/validate",
            json={"code": "LIMITED", "order_total": 1000},
        )
        assert response.status_code == 200
        assert response.json()["valid"] is False


class TestCreatePromo:
    """Tests for POST /promo/ (admin)."""

    def test_create_percent_code(self, client, admin_auth_headers):
        response = client.post(
            "/promo/",
            json={"code": "PCT15", "discount_percent": 15},
            headers=admin_auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["code"] == "PCT15"
        assert data["discount_percent"] == 15

    def test_create_fixed_amount_code(self, client, admin_auth_headers):
        response = client.post(
            "/promo/",
            json={"code": "FIX500", "discount_amount": 500},
            headers=admin_auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["code"] == "FIX500"
        assert data["discount_amount"] == 500

    def test_reject_both_percent_and_amount(self, client, admin_auth_headers):
        response = client.post(
            "/promo/",
            json={"code": "BOTH", "discount_percent": 10, "discount_amount": 500},
            headers=admin_auth_headers,
        )
        assert response.status_code == 400

    def test_reject_neither(self, client, admin_auth_headers):
        response = client.post(
            "/promo/",
            json={"code": "NEITHER"},
            headers=admin_auth_headers,
        )
        assert response.status_code == 400

    def test_duplicate_code_rejected(self, client, admin_auth_headers, test_db):
        _make_promo(test_db, code="DUP", discount_percent=10)
        response = client.post(
            "/promo/",
            json={"code": "dup", "discount_percent": 20},
            headers=admin_auth_headers,
        )
        assert response.status_code == 409

    def test_non_admin_forbidden(self, client, auth_headers):
        response = client.post(
            "/promo/",
            json={"code": "X10", "discount_percent": 10},
            headers=auth_headers,
        )
        assert response.status_code == 403


class TestUpdatePromo:
    """Tests for PUT /promo/{id} (admin)."""

    def test_update_fields(self, client, admin_auth_headers, test_db):
        promo = _make_promo(test_db, code="UPD", discount_percent=10)
        response = client.put(
            f"/promo/{promo.id}",
            json={"discount_percent": 25, "max_uses": 50},
            headers=admin_auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["discount_percent"] == 25
        assert data["max_uses"] == 50

    def test_update_missing_404(self, client, admin_auth_headers):
        response = client.put(
            "/promo/99999",
            json={"discount_percent": 25},
            headers=admin_auth_headers,
        )
        assert response.status_code == 404


class TestDeletePromo:
    """Tests for DELETE /promo/{id} (admin) - soft deactivate."""

    def test_soft_deactivates(self, client, admin_auth_headers, test_db):
        promo = _make_promo(test_db, code="DEL", discount_percent=10)
        promo_id = promo.id

        response = client.delete(f"/promo/{promo_id}", headers=admin_auth_headers)
        assert response.status_code == 204

        # Still present when listing (not hard-deleted), but is_active False
        list_resp = client.get("/promo/", headers=admin_auth_headers)
        assert list_resp.status_code == 200
        codes = {p["id"]: p for p in list_resp.json()}
        assert promo_id in codes
        assert codes[promo_id]["is_active"] is False

    def test_delete_missing_404(self, client, admin_auth_headers):
        response = client.delete("/promo/99999", headers=admin_auth_headers)
        assert response.status_code == 404


class TestListPromo:
    """Tests for GET /promo/ (admin)."""

    def test_list_as_admin(self, client, admin_auth_headers, test_db):
        _make_promo(test_db, code="L1", discount_percent=10)
        _make_promo(test_db, code="L2", discount_amount=300)
        response = client.get("/promo/", headers=admin_auth_headers)
        assert response.status_code == 200
        assert len(response.json()) == 2

    def test_list_non_admin_forbidden(self, client, auth_headers):
        response = client.get("/promo/", headers=auth_headers)
        assert response.status_code == 403
