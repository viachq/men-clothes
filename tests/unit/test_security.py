"""
Unit tests for security functions (password hashing, JWT tokens).
These are critical security components that must work correctly.
"""
import pytest
from datetime import datetime, timedelta, timezone

from backend.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_token
)
from backend.core.config import JWT_EXPIRES_MINUTES


class TestPasswordHashing:
    """Tests for password hashing and verification."""
    
    def test_hash_password_creates_hash(self):
        """Test that password is hashed."""
        password = "test_password_123"
        hashed = hash_password(password)
        
        assert hashed != password
        assert len(hashed) > 0
        assert "$" in hashed  # Format: salt$hash
    
    def test_hash_different_passwords_different_hashes(self):
        """Test that different passwords produce different hashes."""
        hash1 = hash_password("password1")
        hash2 = hash_password("password2")
        
        assert hash1 != hash2
    
    def test_same_password_different_salts(self):
        """Test that same password produces different hashes (different salts)."""
        password = "same_password"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        
        assert hash1 != hash2  # Different salts
    
    def test_verify_correct_password(self):
        """Test verification of correct password."""
        password = "correct_password"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True
    
    def test_verify_incorrect_password(self):
        """Test verification of incorrect password."""
        hashed = hash_password("correct_password")
        
        assert verify_password("wrong_password", hashed) is False
    
    def test_verify_empty_password(self):
        """Test that empty password doesn't pass."""
        hashed = hash_password("some_password")
        
        assert verify_password("", hashed) is False
    
    def test_verify_malformed_hash(self):
        """Test verification with invalid hash."""
        assert verify_password("password", "invalid_hash") is False
        assert verify_password("password", "") is False
    
    @pytest.mark.parametrize("password", [
        "short",
        "very_long_password_" * 100,
        "пароль_українською",
        "password with spaces",
        "p@$$w0rd!#%",
        "emoji_password_🔐",
    ])
    def test_various_password_formats(self, password):
        """Test various password formats."""
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True


class TestJWT:
    """Tests for JWT token creation and validation."""
    
    def test_create_token_contains_subject(self):
        """Test that token is created with username."""
        username = "testuser"
        token = create_access_token(username)
        
        assert token is not None
        assert len(token) > 0
        assert isinstance(token, str)
    
    def test_decode_valid_token(self):
        """Test decoding of valid token."""
        username = "testuser"
        token = create_access_token(username)
        payload = decode_token(token)
        
        assert payload is not None
        assert payload["sub"] == username
        assert "exp" in payload
        assert "iat" in payload
    
    def test_decode_invalid_token(self):
        """Test decoding of invalid token."""
        invalid_token = "invalid.token.here"
        payload = decode_token(invalid_token)
        
        assert payload is None
    
    def test_decode_tampered_token(self):
        """Test that tampered token is rejected."""
        token = create_access_token("user1")
        tampered = token[:-5] + "XXXXX"  # Modify part of token
        
        payload = decode_token(tampered)
        assert payload is None
    
    def test_token_expiration_time(self):
        """Test that token has correct expiration time."""
        token = create_access_token("user")
        payload = decode_token(token)
        
        exp_timestamp = payload["exp"]
        iat_timestamp = payload["iat"]
        
        # Difference should be close to JWT_EXPIRES_MINUTES
        diff_minutes = (exp_timestamp - iat_timestamp) / 60
        assert abs(diff_minutes - JWT_EXPIRES_MINUTES) < 1
    
    @pytest.mark.parametrize("username", [
        "simple_user",
        "user@email.com",
        "user.name",
        "user_123",
        "UPPERCASE",
        "спеціальні-символи",
    ])
    def test_token_with_various_usernames(self, username):
        """Test tokens with different usernames."""
        token = create_access_token(username)
        payload = decode_token(token)
        
        assert payload["sub"] == username
    
    def test_token_is_string(self):
        """Test that token is returned as string."""
        token = create_access_token("user")
        assert isinstance(token, str)
    
    def test_token_has_three_parts(self):
        """Test that JWT has standard format (header.payload.signature)."""
        token = create_access_token("user")
        parts = token.split(".")
        
        assert len(parts) == 3

