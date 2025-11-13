"""Database seed file - creates demo data for testing"""

from app.database import get_db
from app.database.models import Organization, User, Person, Photo
from app.utils.auth import hash_password
from datetime import datetime, timedelta
import random


def seed_demo_data():
    """Create demo organization, users, persons, and sample photos for testing"""
    try:
        with get_db() as db:
            # Check if demo data already exists
            existing_org = db.query(Organization).filter(Organization.name == "Demo Daycare").first()
            if existing_org:
                return  # Demo data already exists

            # Create demo organization
            org = Organization(
                name="Demo Daycare",
                email="demo@daycare.com"
            )
            db.add(org)
            db.flush()  # Get org ID

            # Create demo users
            staff_user = User(
                email="staff@demo.com",
                password_hash=hash_password("password123"),
                role="staff",
                organization_id=org.id
            )

            parent_user = User(
                email="parent@demo.com",
                password_hash=hash_password("password123"),
                role="parent",
                organization_id=org.id
            )

            admin_user = User(
                email="admin@demo.com",
                password_hash=hash_password("password123"),
                role="admin",
                organization_id=org.id
            )

            db.add(staff_user)
            db.add(parent_user)
            db.add(admin_user)
            db.flush()

            # Create demo persons (children)
            persons = [
                Person(name="Emma Johnson", organization_id=org.id),
                Person(name="Noah Smith", organization_id=org.id),
                Person(name="Olivia Brown", organization_id=org.id),
            ]

            for person in persons:
                db.add(person)

            db.flush()  # Get person IDs

            # Create sample photos with AI descriptions
            activities = [
                "Playing with colorful building blocks and creating tall structures",
                "Enjoying healthy snack time with fresh fruits",
                "Reading an exciting picture book about animals",
                "Creating beautiful artwork with paints and brushes",
                "Having fun in the outdoor playground",
                "Taking a peaceful afternoon nap after lunch",
                "Learning numbers and letters through interactive games",
                "Dancing and moving to cheerful music",
                "Sharing lunch with friends at the table",
                "Playing imaginatively with toy vehicles"
            ]

            # Create 3-5 sample photos for each person
            for person in persons:
                num_photos = random.randint(3, 5)
                for i in range(num_photos):
                    days_ago = random.randint(0, 7)
                    hours_ago = random.randint(8, 17)  # Between 8am and 5pm
                    uploaded_time = datetime.now() - timedelta(days=days_ago, hours=hours_ago)

                    photo = Photo(
                        url=f"https://via.placeholder.com/400x300/667eea/ffffff?text={person.name.replace(' ', '+')}",
                        person_id=person.id,
                        ai_description=random.choice(activities),
                        uploaded_by=staff_user.id,
                        organization_id=org.id,
                        uploaded_at=uploaded_time
                    )
                    db.add(photo)

            db.commit()
            print("✅ Demo data created successfully with sample photos!")

    except Exception as e:
        print(f"Note: {e}")
        pass  # Silently fail - data might already exist


if __name__ == "__main__":
    seed_demo_data()
