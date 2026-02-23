"""Tests para las utilidades de contraseña y fecha."""
import pytest
from utils.password import get_password_hash, verify_password
from utils.datetime import time_at
from datetime import datetime, timezone


class TestPasswordUtils:
    def test_hash_returns_string(self):
        hashed = get_password_hash("MiPassword123")
        assert isinstance(hashed, str)

    def test_hash_is_not_plaintext(self):
        plain = "MiPassword123"
        hashed = get_password_hash(plain)
        assert hashed != plain

    def test_verify_correct_password(self):
        plain = "MiPassword123"
        hashed = get_password_hash(plain)
        assert verify_password(plain, hashed) is True

    def test_verify_wrong_password(self):
        hashed = get_password_hash("MiPassword123")
        assert verify_password("OtraPassword456", hashed) is False

    def test_two_hashes_of_same_password_differ(self):
        """bcrypt usa salt aleatorio: dos hashes del mismo texto deben ser distintos."""
        plain = "RepetidaPassword"
        h1 = get_password_hash(plain)
        h2 = get_password_hash(plain)
        assert h1 != h2

    def test_verify_empty_password_returns_false(self):
        hashed = get_password_hash("SomePassword")
        assert verify_password("", hashed) is False

    def test_hash_special_characters(self):
        plain = "P@$$w0rd!#%"
        hashed = get_password_hash(plain)
        assert verify_password(plain, hashed) is True


class TestDatetimeUtils:
    def test_time_at_returns_datetime(self):
        result = time_at()
        assert isinstance(result, datetime)

    def test_time_at_is_utc_aware(self):
        result = time_at()
        assert result.tzinfo is not None
        assert result.utcoffset().total_seconds() == 0

    def test_time_at_millisecond_precision(self):
        """Debe tener precisión de milisegundos (microsegundos múltiplo de 1000)."""
        result = time_at()
        assert result.microsecond % 1000 == 0

    def test_time_at_is_recent(self):
        from datetime import timedelta
        # time_at() trunca a milisegundos, por lo que usamos un margen de ±1 segundo
        before = datetime.now(timezone.utc) - timedelta(seconds=1)
        result = time_at()
        after = datetime.now(timezone.utc) + timedelta(seconds=1)
        assert before <= result <= after
