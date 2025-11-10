"""Database seeding for demo data"""

from app.database import get_db
from app.database.models import Daycare, User, UserRole
from app.utils.auth import hash_password
from datetime import datetime


def seed_demo_data():
    """Seed database with demo daycare and users"""

    with get_db() as db:
        # Check if demo data already exists (check for any demo user)
        existing_user = db.query(User).filter(User.email == "admin@demo.com").first()

        if existing_user:
            # Demo data already exists, skip seeding
            return

        # Create demo daycare
        demo_daycare = Daycare(
            name="Sunny Days Daycare",
            address="123 Main St, Demo City",
            phone="+1-555-0100",
            email="demo@daycare.com",
            license_number="DEMO-2025-001",
            is_active=True,
            timezone="America/New_York"
        )
        db.add(demo_daycare)
        db.flush()  # Get the daycare ID

        # Create demo users
        demo_users = [
            {
                "email": "admin@demo.com",
                "password": "admin123",
                "first_name": "Admin",
                "last_name": "User",
                "role": UserRole.ADMIN,
                "phone": "+1-555-0101"
            },
            {
                "email": "staff@demo.com",
                "password": "staff123",
                "first_name": "Jane",
                "last_name": "Smith",
                "role": UserRole.STAFF,
                "phone": "+1-555-0102"
            },
            {
                "email": "parent@demo.com",
                "password": "parent123",
                "first_name": "John",
                "last_name": "Doe",
                "role": UserRole.PARENT,
                "phone": "+1-555-0103"
            }
        ]

        for user_data in demo_users:
            user = User(
                email=user_data["email"],
                password_hash=hash_password(user_data["password"]),
                first_name=user_data["first_name"],
                last_name=user_data["last_name"],
                role=user_data["role"],
                phone=user_data.get("phone"),
                daycare_id=demo_daycare.id,
                is_active=True
            )
            db.add(user)

        db.commit()
        # Silently seed without print statements (for production)


if __name__ == "__main__":
    from app.database import init_db
    init_db()
    seed_demo_data()
