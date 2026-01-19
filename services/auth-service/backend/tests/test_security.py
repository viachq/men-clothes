"""
Tests for security functions (password hashing, JWT tokens).
"""
import time
from datetime import timedelta

import pytest
from jose import jwt

from backend.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_token,
)
from backend.core.config import JWT_SECRET_KEY, JWT_ALGORITHM


class TestHashPassword:
    """Tests for hash_password function."""

    def test_hash_password_creates_hash(self):
        """Test that hash_password creates a hash."""
        password = "testpassword123"
        hashed = hash_password(password)
        assert hashed is not None
        assert len(hashed) > 0
        assert hashed != password

    def test_hash_password_contains_salt_and_hash(self):
        """Test that hash contains salt and hash separated by $."""
        password = "testpassword123"
        hashed = hash_password(password)
        assert '$' in hashed
        parts = hashed.split('$')
        assert len(parts) == 2
        assert len(parts[0]) > 0  # salt
        assert len(parts[1]) > 0  # hash

    def test_hash_password_different_passwords_different_hashes(self):
        """Test that different passwords produce different hashes."""
        password1 = "password1"
        password2 = "password2"
        hashed1 = hash_password(password1)
        hashed2 = hash_password(password2)
        assert hashed1 != hashed2

    def test_hash_password_same_password_different_hashes(self):
        """Test that same password produces different hashes (due to salt)."""
        password = "samepassword"
        hashed1 = hash_password(password)
        hashed2 = hash_password(password)
        # Hashes should be different due to random salt
        assert hashed1 != hashed2


class TestVerifyPassword:
    """Tests for verify_password function."""

    def test_verify_password_correct_password(self):
        """Test that correct password returns True."""
        password = "testpassword123"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect_password(self):
        """Test that incorrect password returns False."""
        password = "testpassword123"
        wrong_password = "wrongpassword"
        hashed = hash_password(password)
        assert verify_password(wrong_password, hashed) is False

    def test_verify_password_legacy_password(self):
        """Test backwards compatibility with legacy passwords without salt."""
        import hashlib
        password = "legacypassword"
        # Legacy format: just SHA256 hash without salt
        legacy_hash = hashlib.sha256(password.encode()).hexdigest()
        assert verify_password(password, legacy_hash) is True
        assert verify_password("wrong", legacy_hash) is False

    def test_verify_password_invalid_format(self):
        """Test that invalid hash format returns False."""
        password = "testpassword"
        invalid_hash = "notavalidhashformat"
        assert verify_password(password, invalid_hash) is False

    def test_verify_password_empty_password(self):
        """Test verification with empty password."""
        hashed = hash_password("")
        assert verify_password("", hashed) is True
        assert verify_password("notempty", hashed) is False


class TestCreateAccessToken:
    """Tests for create_access_token function."""

    def test_create_access_token_creates_token(self):
        """Test that token is created successfully."""
        username = "testuser"
        token = create_access_token(username)
        assert token is not None
        assert len(token) > 0

    def test_create_access_token_contains_subject(self):
        """Test that token contains correct subject (username)."""
        username = "testuser"
        token = create_access_token(username)
        payload = decode_token(token)
        assert payload is not None
        assert payload["sub"] == username

    def test_create_access_token_contains_exp(self):
        """Test that token contains expiration claim."""
        username = "testuser"
        token = create_access_token(username)
        payload = decode_token(token)
        assert payload is not None
        assert "exp" in payload
        assert payload["exp"] > int(time.time())

    def test_create_access_token_contains_iat(self):
        """Test that token contains issued at claim."""
        username = "testuser"
        token = create_access_token(username)
        payload = decode_token(token)
        assert payload is not None
        assert "iat" in payload

    def test_create_access_token_different_users_different_tokens(self):
        """Test that different users get different tokens."""
        username1 = "user1"
        username2 = "user2"
        token1 = create_access_token(username1)
        token2 = create_access_token(username2)
        assert token1 != token2


class TestDecodeToken:
    """Tests for decode_token function."""

    def test_decode_token_valid_token(self):
        """Test that valid token is decoded correctly."""
        username = "testuser"
        token = create_access_token(username)
        payload = decode_token(token)
        assert payload is not None
        assert payload["sub"] == username
        assert "exp" in payload
        assert "iat" in payload

    def test_decode_token_invalid_token(self):
        """Test that invalid token returns None."""
        invalid_token = "invalid.token.here"
        payload = decode_token(invalid_token)
        assert payload is None

    def test_decode_token_wrong_secret(self):
        """Test that token with wrong secret returns None."""
        username = "testuser"
        token = create_access_token(username)
        # Try to decode with wrong secret
        try:
            payload = jwt.decode(
                token,
                "wrong-secret-key",
                algorithms=[JWT_ALGORITHM]
            )
            # If it decodes, the payload should not match
            assert payload["sub"] != username
        except jwt.JWTError:
            # Expected behavior - should raise JWTError
            pass

    def test_decode_token_expired_token(self):
        """Test that expired token returns None."""
        from datetime import datetime, timezone, timedelta
        # Create an expired token manually
        expire = datetime.now(timezone.utc) - timedelta(minutes=1)
        to_encode = {
            "sub": "testuser",
            "exp": expire,
            "iat": datetime.now(timezone.utc)
        }
        expired_token = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        payload = decode_token(expired_token)
        assert payload is None

    def test_decode_token_empty_string(self):
        """Test that empty string token returns None."""
        payload = decode_token("")
        assert payload is None

    def test_decode_token_none(self):
        """Test that None token returns None."""
        payload = decode_token(None)
        assert payload is None
