"""Test authentication module"""

import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.utils.auth import hash_password, verify_password, register_user, authenticate_user
from app.database import init_db, get_db
from app.database.models import User


@pytest.fixture(scope="module")
def setup_db():
    """Setup test database"""
    init_db()
    yield
    # Cleanup handled by SQLite in-memory database


def test_password_hashing():
    """Test password hashing and verification"""
    password = "test123"
    hashed = hash_password(password)

    assert hashed != password
    assert verify_password(password, hashed) == True
    assert verify_password("wrong", hashed) == False


def test_user_registration(setup_db):
    """Test user registration"""
    user, error = register_user(
        email="test@example.com",
        password="test123",
        first_name="Test",
        last_name="User",
        role="parent",
        daycare_id="test-daycare-id"
    )

    assert user is not None
    assert user.email == "test@example.com"
    assert user.first_name == "Test"
    assert error is None


def test_duplicate_registration(setup_db):
    """Test duplicate email registration"""
    # First registration
    user1, error1 = register_user(
        email="duplicate@example.com",
        password="test123",
        first_name="User",
        last_name="One",
        role="parent",
        daycare_id="test-daycare-id"
    )

    assert user1 is not None

    # Duplicate registration
    user2, error2 = register_user(
        email="duplicate@example.com",
        password="test456",
        first_name="User",
        last_name="Two",
        role="parent",
        daycare_id="test-daycare-id"
    )

    assert user2 is None
    assert error2 is not None


def test_authentication(setup_db):
    """Test user authentication"""
    # Register user
    register_user(
        email="auth@example.com",
        password="auth123",
        first_name="Auth",
        last_name="Test",
        role="staff",
        daycare_id="test-daycare-id"
    )

    # Correct credentials
    user = authenticate_user("auth@example.com", "auth123")
    assert user is not None
    assert user.email == "auth@example.com"

    # Wrong password
    user = authenticate_user("auth@example.com", "wrongpass")
    assert user is None

    # Non-existent user
    user = authenticate_user("nonexistent@example.com", "password")
    assert user is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
