import pytest
from datetime import datetime, timedelta, timezone

from app.security.authentication import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
    _get_secret_key,
)


class TestPasswordHashing:
    def test_hash_password_returns_string(self):
        hashed = hash_password("testpassword")
        assert isinstance(hashed, str)
        assert hashed != "testpassword"

    def test_verify_password_correct(self):
        hashed = hash_password("mypassword")
        assert verify_password("mypassword", hashed) is True

    def test_verify_password_incorrect(self):
        hashed = hash_password("mypassword")
        assert verify_password("wrongpassword", hashed) is False


class TestJWT:
    def test_create_and_decode_token(self):
        data = {"sub": "user@example.com", "role": "citizen"}
        token = create_access_token(data)
        decoded = decode_access_token(token)
        assert decoded is not None
        assert decoded["sub"] == "user@example.com"
        assert decoded["role"] == "citizen"
        assert "exp" in decoded

    def test_expired_token_returns_none(self):
        data = {"sub": "user@example.com"}
        token = create_access_token(data, expires_delta=timedelta(seconds=-1))
        decoded = decode_access_token(token)
        assert decoded is None

    def test_invalid_token_returns_none(self):
        decoded = decode_access_token("not.a.valid.token")
        assert decoded is None

    def test_secret_key_required(self):
        import app.config as config_mod
        original = config_mod.settings.JWT_SECRET_KEY
        try:
            config_mod.settings.JWT_SECRET_KEY = ""
            with pytest.raises(RuntimeError, match="JWT_SECRET_KEY"):
                _get_secret_key()
        finally:
            config_mod.settings.JWT_SECRET_KEY = original
