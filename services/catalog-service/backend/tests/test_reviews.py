"""
Tests for product reviews endpoints.
"""
import pytest

from backend.models.review import ProductReview


class TestGetProductReviews:
    """Tests for GET /reviews/product/{id}."""

    def test_empty_when_none(self, client, test_menu_item):
        response = client.get(f"/reviews/product/{test_menu_item.id}")
        assert response.status_code == 200
        assert response.json() == []

    def test_returns_reviews_when_present(self, client, test_menu_item, test_db):
        review = ProductReview(
            product_id=test_menu_item.id,
            user_id=1,
            username="testuser",
            rating=5,
            comment="Great product",
        )
        test_db.add(review)
        test_db.commit()

        response = client.get(f"/reviews/product/{test_menu_item.id}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["rating"] == 5
        assert data[0]["comment"] == "Great product"
        assert data[0]["username"] == "testuser"


class TestCreateReview:
    """Tests for POST /reviews/product/{id}."""

    def test_create_review_authenticated(self, client, auth_headers, test_menu_item):
        response = client.post(
            f"/reviews/product/{test_menu_item.id}",
            json={"rating": 4, "comment": "Nice"},
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["rating"] == 4
        assert data["comment"] == "Nice"
        assert data["product_id"] == test_menu_item.id
        assert data["user_id"] == 1

    def test_create_review_missing_product(self, client, auth_headers):
        response = client.post(
            "/reviews/product/99999",
            json={"rating": 4, "comment": "Nice"},
            headers=auth_headers,
        )
        assert response.status_code == 404

    def test_create_review_unauthenticated(self, client, test_menu_item):
        response = client.post(
            f"/reviews/product/{test_menu_item.id}",
            json={"rating": 4, "comment": "Nice"},
        )
        assert response.status_code == 401

    def test_create_duplicate_review_rejected(self, client, auth_headers, test_menu_item):
        first = client.post(
            f"/reviews/product/{test_menu_item.id}",
            json={"rating": 4, "comment": "First"},
            headers=auth_headers,
        )
        assert first.status_code == 201

        second = client.post(
            f"/reviews/product/{test_menu_item.id}",
            json={"rating": 3, "comment": "Second"},
            headers=auth_headers,
        )
        assert second.status_code == 400


class TestCanReview:
    """Tests for GET /reviews/can-review/{id}."""

    def test_can_review_true_when_not_reviewed(self, client, auth_headers, test_menu_item):
        response = client.get(
            f"/reviews/can-review/{test_menu_item.id}",
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["can_review"] is True

    def test_can_review_false_after_reviewing(self, client, auth_headers, test_menu_item):
        create = client.post(
            f"/reviews/product/{test_menu_item.id}",
            json={"rating": 5, "comment": "Reviewed"},
            headers=auth_headers,
        )
        assert create.status_code == 201

        response = client.get(
            f"/reviews/can-review/{test_menu_item.id}",
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["can_review"] is False


class TestDeleteReview:
    """Tests for DELETE /reviews/{id}."""

    def _make_review(self, test_db, product_id, user_id, username):
        review = ProductReview(
            product_id=product_id,
            user_id=user_id,
            username=username,
            rating=4,
            comment="To delete",
        )
        test_db.add(review)
        test_db.commit()
        test_db.refresh(review)
        return review

    def test_owner_can_delete(self, client, auth_headers, test_menu_item, test_db):
        review = self._make_review(test_db, test_menu_item.id, 1, "testuser")
        response = client.delete(f"/reviews/{review.id}", headers=auth_headers)
        assert response.status_code == 204

    def test_non_owner_non_admin_forbidden(self, client, auth_headers, test_menu_item, test_db):
        # Review owned by a different user (id=99)
        review = self._make_review(test_db, test_menu_item.id, 99, "otheruser")
        response = client.delete(f"/reviews/{review.id}", headers=auth_headers)
        assert response.status_code == 403

    def test_admin_can_delete_any(self, client, admin_auth_headers, test_menu_item, test_db):
        review = self._make_review(test_db, test_menu_item.id, 99, "otheruser")
        response = client.delete(f"/reviews/{review.id}", headers=admin_auth_headers)
        assert response.status_code == 204

    def test_manager_can_delete_any(self, client, manager_auth_headers, test_menu_item, test_db):
        review = self._make_review(test_db, test_menu_item.id, 99, "otheruser")
        response = client.delete(f"/reviews/{review.id}", headers=manager_auth_headers)
        assert response.status_code == 204

    def test_delete_missing_review_404(self, client, auth_headers):
        response = client.delete("/reviews/99999", headers=auth_headers)
        assert response.status_code == 404
