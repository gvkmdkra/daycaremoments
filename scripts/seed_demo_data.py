"""Seed demo data for testing"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import init_db, get_db
from app.database.models import Daycare, User, Child, Photo, Activity, Subscription, UserRole, PhotoStatus
from app.utils.auth import hash_password
from datetime import datetime, timedelta
import uuid


def seed_demo_data():
    """Create demo data for testing"""

    print("Seeding demo data...")

    # Initialize database
    init_db()

    with get_db() as db:
        # 1. Create demo daycare
        print("  Creating demo daycare...")
        daycare = Daycare(
            id=str(uuid.uuid4()),
            name="Sunshine Kids Daycare",
            email="contact@sunshinekids.com",
            phone="555-123-4567",
            address="123 Happy Street, Sunnyville, CA 90210",
            license_number="CA-DAYCARE-12345",
            is_active=True,
            created_at=datetime.utcnow()
        )
        db.add(daycare)
        db.flush()

        # 2. Create demo users
        print("  Creating demo users...")

        # Admin
        admin = User(
            id=str(uuid.uuid4()),
            email="admin@demo.com",
            password_hash=hash_password("admin123"),
            first_name="Admin",
            last_name="User",
            role=UserRole.ADMIN,
            daycare_id=daycare.id,
            phone="555-100-0001",
            created_at=datetime.utcnow()
        )
        db.add(admin)

        # Staff
        staff = User(
            id=str(uuid.uuid4()),
            email="staff@demo.com",
            password_hash=hash_password("staff123"),
            first_name="Jane",
            last_name="Teacher",
            role=UserRole.STAFF,
            daycare_id=daycare.id,
            phone="555-100-0002",
            created_at=datetime.utcnow()
        )
        db.add(staff)

        # Parents
        parent1 = User(
            id=str(uuid.uuid4()),
            email="parent@demo.com",
            password_hash=hash_password("parent123"),
            first_name="John",
            last_name="Smith",
            role=UserRole.PARENT,
            daycare_id=daycare.id,
            phone="555-100-0003",
            created_at=datetime.utcnow()
        )
        db.add(parent1)

        parent2 = User(
            id=str(uuid.uuid4()),
            email="sarah@demo.com",
            password_hash=hash_password("parent123"),
            first_name="Sarah",
            last_name="Johnson",
            role=UserRole.PARENT,
            daycare_id=daycare.id,
            phone="555-100-0004",
            created_at=datetime.utcnow()
        )
        db.add(parent2)

        db.flush()

        # 3. Create demo children
        print("  Creating demo children...")

        child1 = Child(
            id=str(uuid.uuid4()),
            first_name="Emma",
            last_name="Smith",
            date_of_birth=datetime(2021, 5, 15).date(),
            parent_id=parent1.id,
            daycare_id=daycare.id,
            allergies="Peanuts",
            medical_notes="EpiPen in office",
            created_at=datetime.utcnow()
        )
        db.add(child1)

        child2 = Child(
            id=str(uuid.uuid4()),
            first_name="Lucas",
            last_name="Johnson",
            date_of_birth=datetime(2022, 3, 22).date(),
            parent_id=parent2.id,
            daycare_id=daycare.id,
            created_at=datetime.utcnow()
        )
        db.add(child2)

        child3 = Child(
            id=str(uuid.uuid4()),
            first_name="Olivia",
            last_name="Smith",
            date_of_birth=datetime(2023, 1, 10).date(),
            parent_id=parent1.id,
            daycare_id=daycare.id,
            created_at=datetime.utcnow()
        )
        db.add(child3)

        db.flush()

        # 4. Create demo photos
        print("  Creating demo photos...")

        for i in range(10):
            photo = Photo(
                id=str(uuid.uuid4()),
                url=f"https://picsum.photos/400/300?random={i}",
                child_id=child1.id if i % 2 == 0 else child2.id,
                daycare_id=daycare.id,
                uploaded_by=staff.id,
                caption=f"Having fun at {['art class', 'playtime', 'outdoor time', 'story time'][i % 4]}!",
                activity_type=["art", "play", "outdoor", "learning"][i % 4],
                status=PhotoStatus.APPROVED,
                uploaded_at=datetime.utcnow() - timedelta(days=i),
                created_at=datetime.utcnow()
            )
            db.add(photo)

        # 5. Create demo activities
        print("  Creating demo activities...")

        activity_types = ["meal", "nap", "play", "learning", "outdoor", "art"]
        today = datetime.now().date()

        for i in range(15):
            activity = Activity(
                id=str(uuid.uuid4()),
                child_id=[child1.id, child2.id, child3.id][i % 3],
                daycare_id=daycare.id,
                staff_id=staff.id,
                activity_type=activity_types[i % len(activity_types)],
                activity_time=datetime.combine(today, datetime.min.time()) + timedelta(hours=9 + i % 8, minutes=i * 5),
                duration_minutes=[30, 60, 90, 15, 45][i % 5],
                notes=f"Great participation! {['Loved it!', 'Very engaged', 'Had fun', 'Asked for more'][i % 4]}",
                mood=["😊 Happy", "🤩 Excited", "🙂 Good"][i % 3],
                created_at=datetime.utcnow()
            )
            db.add(activity)

        # 6. Create demo subscription
        print("  Creating demo subscription...")

        subscription = Subscription(
            id=str(uuid.uuid4()),
            daycare_id=daycare.id,
            plan_name="pro",
            status="trial",
            price=79,
            billing_cycle="monthly",
            trial_end_date=datetime.now() + timedelta(days=14),
            next_billing_date=datetime.now() + timedelta(days=14),
            created_at=datetime.utcnow()
        )
        db.add(subscription)

        db.commit()

    print("\n✅ Demo data seeded successfully!\n")
    print("=" * 60)
    print("Demo Accounts:")
    print("=" * 60)
    print("\n👑 ADMIN:")
    print("   Email: admin@demo.com")
    print("   Password: admin123")
    print("\n👨‍🏫 STAFF:")
    print("   Email: staff@demo.com")
    print("   Password: staff123")
    print("\n👪 PARENT:")
    print("   Email: parent@demo.com")
    print("   Password: parent123")
    print("   Children: Emma Smith, Olivia Smith")
    print("\n👪 PARENT 2:")
    print("   Email: sarah@demo.com")
    print("   Password: parent123")
    print("   Child: Lucas Johnson")
    print("\n" + "=" * 60)
    print("✅ Ready to test! Run: streamlit run app.py")
    print("=" * 60)


if __name__ == "__main__":
    seed_demo_data()
