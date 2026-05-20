"""
Tests for product variant endpoints.
"""
import pytest

from backend.models.product_variant import ProductVariant


class TestListVariants:
    """Tests for GET /variants/product/{id}."""

    def test_empty_list(self, client, test_menu_item):
        response = client.get(f"/variants/product/{test_menu_item.id}")
        assert response.status_code == 200
        assert response.json() == []

    def test_list_with_variants(self, client, test_menu_item, test_db):
        v1 = ProductVariant(menu_item_id=test_menu_item.id, size="S", stock=5)
        v2 = ProductVariant(menu_item_id=test_menu_item.id, size="M", stock=10)
        test_db.add_all([v1, v2])
        test_db.commit()

        response = client.get(f"/variants/product/{test_menu_item.id}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        sizes = {v["size"]: v["stock"] for v in data}
        assert sizes == {"S": 5, "M": 10}

    def test_list_missing_product_404(self, client):
        response = client.get("/variants/product/99999")
        assert response.status_code == 404


class TestCreateVariant:
    """Tests for POST /variants/product/{id}."""

    def test_admin_creates_variant(self, client, admin_auth_headers, test_menu_item):
        response = client.post(
            f"/variants/product/{test_menu_item.id}",
            json={"size": "L", "stock": 7},
            headers=admin_auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["size"] == "L"
        assert data["stock"] == 7
        assert data["menu_item_id"] == test_menu_item.id

    def test_manager_creates_variant(self, client, manager_auth_headers, test_menu_item):
        response = client.post(
            f"/variants/product/{test_menu_item.id}",
            json={"size": "xl", "stock": 3},
            headers=manager_auth_headers,
        )
        assert response.status_code == 201
        assert response.json()["size"] == "XL"

    def test_client_forbidden(self, client, auth_headers, test_menu_item):
        response = client.post(
            f"/variants/product/{test_menu_item.id}",
            json={"size": "M", "stock": 1},
            headers=auth_headers,
        )
        assert response.status_code == 403

    def test_duplicate_size_rejected(self, client, admin_auth_headers, test_menu_item, test_db):
        existing = ProductVariant(menu_item_id=test_menu_item.id, size="M", stock=2)
        test_db.add(existing)
        test_db.commit()

        response = client.post(
            f"/variants/product/{test_menu_item.id}",
            json={"size": "m", "stock": 9},
            headers=admin_auth_headers,
        )
        assert response.status_code == 409

    def test_create_missing_product_404(self, client, admin_auth_headers):
        response = client.post(
            "/variants/product/99999",
            json={"size": "M", "stock": 1},
            headers=admin_auth_headers,
        )
        assert response.status_code == 404


class TestUpdateVariant:
    """Tests for PUT /variants/{id}."""

    def _make_variant(self, test_db, product_id):
        variant = ProductVariant(menu_item_id=product_id, size="M", stock=5)
        test_db.add(variant)
        test_db.commit()
        test_db.refresh(variant)
        return variant

    def test_admin_updates_stock(self, client, admin_auth_headers, test_menu_item, test_db):
        variant = self._make_variant(test_db, test_menu_item.id)
        response = client.put(
            f"/variants/{variant.id}",
            json={"stock": 42},
            headers=admin_auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["stock"] == 42

    def test_manager_updates_stock(self, client, manager_auth_headers, test_menu_item, test_db):
        variant = self._make_variant(test_db, test_menu_item.id)
        response = client.put(
            f"/variants/{variant.id}",
            json={"stock": 0},
            headers=manager_auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["stock"] == 0

    def test_client_forbidden(self, client, auth_headers, test_menu_item, test_db):
        variant = self._make_variant(test_db, test_menu_item.id)
        response = client.put(
            f"/variants/{variant.id}",
            json={"stock": 99},
            headers=auth_headers,
        )
        assert response.status_code == 403

    def test_update_missing_variant_404(self, client, admin_auth_headers):
        response = client.put(
            "/variants/99999",
            json={"stock": 1},
            headers=admin_auth_headers,
        )
        assert response.status_code == 404


class TestDeleteVariant:
    """Tests for DELETE /variants/{id}."""

    def _make_variant(self, test_db, product_id):
        variant = ProductVariant(menu_item_id=product_id, size="M", stock=5)
        test_db.add(variant)
        test_db.commit()
        test_db.refresh(variant)
        return variant

    def test_admin_deletes(self, client, admin_auth_headers, test_menu_item, test_db):
        variant = self._make_variant(test_db, test_menu_item.id)
        response = client.delete(f"/variants/{variant.id}", headers=admin_auth_headers)
        assert response.status_code == 204

    def test_manager_deletes(self, client, manager_auth_headers, test_menu_item, test_db):
        variant = self._make_variant(test_db, test_menu_item.id)
        response = client.delete(f"/variants/{variant.id}", headers=manager_auth_headers)
        assert response.status_code == 204

    def test_client_forbidden(self, client, auth_headers, test_menu_item, test_db):
        variant = self._make_variant(test_db, test_menu_item.id)
        response = client.delete(f"/variants/{variant.id}", headers=auth_headers)
        assert response.status_code == 403

    def test_delete_missing_variant_404(self, client, admin_auth_headers):
        response = client.delete("/variants/99999", headers=admin_auth_headers)
        assert response.status_code == 404
