"""Test database models and operations"""

import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import init_db, get_db
from app.database.models import Daycare, User, Child, Photo, Activity, UserRole, PhotoStatus
from datetime import datetime
import uuid


@pytest.fixture(scope="module")
def setup_db():
    """Setup test database"""
    init_db()
    yield


def test_daycare_creation(setup_db):
    """Test creating a daycare"""
    with get_db() as db:
        daycare = Daycare(
            id=str(uuid.uuid4()),
            name="Test Daycare",
            email="test@daycare.com",
            license_number="TEST-001",
            created_at=datetime.utcnow()
        )
        db.add(daycare)
        db.commit()

        # Verify
        found = db.query(Daycare).filter(Daycare.name == "Test Daycare").first()
        assert found is not None
        assert found.email == "test@daycare.com"


def test_user_creation(setup_db):
    """Test creating users"""
    with get_db() as db:
        daycare = db.query(Daycare).first()

        user = User(
            id=str(uuid.uuid4()),
            email="user@test.com",
            password_hash="hashed",
            first_name="Test",
            last_name="User",
            role=UserRole.PARENT,
            daycare_id=daycare.id,
            created_at=datetime.utcnow()
        )
        db.add(user)
        db.commit()

        # Verify
        found = db.query(User).filter(User.email == "user@test.com").first()
        assert found is not None
        assert found.role == UserRole.PARENT


def test_child_creation(setup_db):
    """Test creating children"""
    with get_db() as db:
        parent = db.query(User).filter(User.role == UserRole.PARENT).first()
        daycare = db.query(Daycare).first()

        child = Child(
            id=str(uuid.uuid4()),
            first_name="Test",
            last_name="Child",
            date_of_birth=datetime(2020, 1, 1).date(),
            parent_id=parent.id,
            daycare_id=daycare.id,
            created_at=datetime.utcnow()
        )
        db.add(child)
        db.commit()

        # Verify
        found = db.query(Child).filter(Child.first_name == "Test").first()
        assert found is not None
        assert found.parent_id == parent.id


def test_photo_creation(setup_db):
    """Test creating photos"""
    with get_db() as db:
        child = db.query(Child).first()
        daycare = db.query(Daycare).first()

        photo = Photo(
            id=str(uuid.uuid4()),
            url="https://example.com/photo.jpg",
            child_id=child.id,
            daycare_id=daycare.id,
            status=PhotoStatus.APPROVED,
            uploaded_at=datetime.utcnow(),
            created_at=datetime.utcnow()
        )
        db.add(photo)
        db.commit()

        # Verify
        found = db.query(Photo).filter(Photo.child_id == child.id).first()
        assert found is not None
        assert found.status == PhotoStatus.APPROVED


def test_activity_logging(setup_db):
    """Test logging activities"""
    with get_db() as db:
        child = db.query(Child).first()
        daycare = db.query(Daycare).first()

        activity = Activity(
            id=str(uuid.uuid4()),
            child_id=child.id,
            daycare_id=daycare.id,
            activity_type="meal",
            activity_time=datetime.utcnow(),
            notes="Had a great meal!",
            created_at=datetime.utcnow()
        )
        db.add(activity)
        db.commit()

        # Verify
        found = db.query(Activity).filter(Activity.child_id == child.id).first()
        assert found is not None
        assert found.activity_type == "meal"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
