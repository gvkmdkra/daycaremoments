"""Quick demo data seeder"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import init_db, get_db
from app.database.models import Daycare, User, Child, UserRole
from app.utils.auth import hash_password
from datetime import datetime
import uuid

print("Seeding demo data...")
init_db()

with get_db() as db:
    # Create daycare
    daycare = Daycare(
        id=str(uuid.uuid4()),
        name="Sunshine Kids Daycare",
        email="contact@sunshinekids.com",
        phone="555-123-4567",
        license_number="CA-001"
    )
    db.add(daycare)
    db.flush()

    # Create admin
    admin = User(
        id=str(uuid.uuid4()),
        email="admin@demo.com",
        password_hash=hash_password("admin123"),
        first_name="Admin",
        last_name="User",
        role=UserRole.ADMIN,
        daycare_id=daycare.id
    )
    db.add(admin)

    # Create staff
    staff = User(
        id=str(uuid.uuid4()),
        email="staff@demo.com",
        password_hash=hash_password("staff123"),
        first_name="Jane",
        last_name="Teacher",
        role=UserRole.STAFF,
        daycare_id=daycare.id
    )
    db.add(staff)

    # Create parent
    parent = User(
        id=str(uuid.uuid4()),
        email="parent@demo.com",
        password_hash=hash_password("parent123"),
        first_name="John",
        last_name="Smith",
        role=UserRole.PARENT,
        daycare_id=daycare.id
    )
    db.add(parent)
    db.flush()

    # Create child
    child = Child(
        id=str(uuid.uuid4()),
        first_name="Emma",
        last_name="Smith",
        date_of_birth=datetime(2021, 5, 15).date(),
        parent_id=parent.id,
        daycare_id=daycare.id
    )
    db.add(child)

    db.commit()

print("\nDemo data created successfully!")
print("=" * 60)
print("Demo Accounts:")
print("=" * 60)
print("\nADMIN:  admin@demo.com  / admin123")
print("STAFF:  staff@demo.com  / staff123")
print("PARENT: parent@demo.com / parent123")
print("\n" + "=" * 60)
print("Ready to launch!")
print("Run: streamlit run app.py")
print("=" * 60)
