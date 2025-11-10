"""Database seeding for demo data"""

from app.database import get_db
from app.database.models import Daycare, User, UserRole, Child, Photo, PhotoStatus, Activity
from app.utils.auth import hash_password
from datetime import datetime, date, timedelta
import random


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

        users_dict = {}
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
            users_dict[user_data["role"]] = user

        db.flush()  # Get user IDs

        # Create 10 demo children with realistic details
        demo_children = [
            {
                "first_name": "Emma",
                "last_name": "Johnson",
                "date_of_birth": date(2021, 3, 15),
                "gender": "Female",
                "allergies": "Peanuts",
                "medical_notes": "Asthma inhaler as needed"
            },
            {
                "first_name": "Liam",
                "last_name": "Williams",
                "date_of_birth": date(2021, 7, 22),
                "gender": "Male",
                "allergies": "None",
                "medical_notes": ""
            },
            {
                "first_name": "Olivia",
                "last_name": "Brown",
                "date_of_birth": date(2020, 11, 8),
                "gender": "Female",
                "allergies": "Dairy",
                "medical_notes": "Lactose intolerant"
            },
            {
                "first_name": "Noah",
                "last_name": "Davis",
                "date_of_birth": date(2022, 1, 30),
                "gender": "Male",
                "allergies": "None",
                "medical_notes": ""
            },
            {
                "first_name": "Ava",
                "last_name": "Miller",
                "date_of_birth": date(2021, 5, 12),
                "gender": "Female",
                "allergies": "Eggs",
                "medical_notes": "Mild egg allergy"
            },
            {
                "first_name": "Ethan",
                "last_name": "Wilson",
                "date_of_birth": date(2020, 9, 25),
                "gender": "Male",
                "allergies": "None",
                "medical_notes": ""
            },
            {
                "first_name": "Sophia",
                "last_name": "Moore",
                "date_of_birth": date(2021, 12, 3),
                "gender": "Female",
                "allergies": "None",
                "medical_notes": ""
            },
            {
                "first_name": "Mason",
                "last_name": "Taylor",
                "date_of_birth": date(2022, 4, 18),
                "gender": "Male",
                "allergies": "Shellfish",
                "medical_notes": "Severe shellfish allergy"
            },
            {
                "first_name": "Isabella",
                "last_name": "Anderson",
                "date_of_birth": date(2021, 8, 7),
                "gender": "Female",
                "allergies": "None",
                "medical_notes": ""
            },
            {
                "first_name": "Lucas",
                "last_name": "Thomas",
                "date_of_birth": date(2020, 6, 14),
                "gender": "Male",
                "allergies": "Gluten",
                "medical_notes": "Celiac disease"
            }
        ]

        parent_user = users_dict[UserRole.PARENT]
        children_list = []

        for child_data in demo_children:
            child = Child(
                first_name=child_data["first_name"],
                last_name=child_data["last_name"],
                date_of_birth=child_data["date_of_birth"],
                gender=child_data["gender"],
                allergies=child_data["allergies"],
                medical_notes=child_data["medical_notes"],
                emergency_contact={
                    "name": f"{parent_user.first_name} {parent_user.last_name}",
                    "phone": parent_user.phone,
                    "relationship": "Parent"
                },
                parent_id=parent_user.id,
                daycare_id=demo_daycare.id,
                is_active=True
            )
            db.add(child)
            children_list.append(child)

        db.flush()  # Get child IDs

        # Create demo photos for children with AI-analyzed activities
        # Using child-friendly placeholder images that simulate real daycare photos
        photo_activities = ["Playing", "Lunch Time", "Nap Time", "Art Class", "Outdoor Play", "Story Time", "Music Class", "Learning"]

        # Import photo analysis service
        from app.services.photo_analysis import get_photo_analysis_service
        photo_analyzer = get_photo_analysis_service()

        for i, child in enumerate(children_list):
            # Create 2-4 photos per child
            num_photos = random.randint(2, 4)
            for j in range(num_photos):
                days_ago = random.randint(0, 7)

                # Use baby/child-themed photos from various sources
                # These are publicly available child-safe images
                photo_sources = [
                    f"https://images.pexels.com/photos/1166394/pexels-photo-1166394.jpeg?auto=compress&cs=tinysrgb&w=400&h=300",  # Child playing
                    f"https://images.pexels.com/photos/1648387/pexels-photo-1648387.jpeg?auto=compress&cs=tinysrgb&w=400&h=300",  # Child with toys
                    f"https://images.pexels.com/photos/1648377/pexels-photo-1648377.jpeg?auto=compress&cs=tinysrgb&w=400&h=300",  # Child eating
                    f"https://images.pexels.com/photos/1416736/pexels-photo-1416736.jpeg?auto=compress&cs=tinysrgb&w=400&h=300",  # Child learning
                    f"https://images.pexels.com/photos/1648360/pexels-photo-1648360.jpeg?auto=compress&cs=tinysrgb&w=400&h=300",  # Child outdoor
                ]

                # Pick random photo or use picsum as fallback
                photo_id = (i * 10) + j + 100
                photo_url = random.choice(photo_sources) if random.random() > 0.5 else f"https://picsum.photos/seed/{photo_id}/400/300"

                # Select activity and create caption
                activity_type = random.choice(photo_activities)
                caption = f"{child.first_name} {activity_type}"

                # AI Analysis: Automatically detect activity from photo caption
                analysis = photo_analyzer.analyze_photo(photo_url, {
                    "original_file_name": f"{child.first_name}_Photo_{j+1}.jpg",
                    "caption": caption,
                    "captured_at": datetime.utcnow() - timedelta(days=days_ago)
                })

                photo = Photo(
                    file_name=f"{child.first_name.lower()}_photo_{j+1}.jpg",
                    original_file_name=f"{child.first_name}_Photo_{j+1}.jpg",
                    url=photo_url,
                    thumbnail_url=photo_url.replace("/400/300", "/150/150") if "picsum" in photo_url else photo_url,
                    caption=caption,
                    captured_at=datetime.utcnow() - timedelta(days=days_ago),
                    uploaded_by=users_dict[UserRole.STAFF].id,
                    child_id=child.id,
                    daycare_id=demo_daycare.id,
                    status=PhotoStatus.APPROVED,
                    approved_by=users_dict[UserRole.ADMIN].id
                )
                db.add(photo)

        db.flush()  # Get photo IDs

        # Create demo activities for today
        activity_types = ["meal", "nap", "play", "learning", "outdoor", "art"]
        moods = ["😊 Happy", "🙂 Good", "😐 Okay", "🤩 Excited"]
        activity_notes = {
            "meal": ["Ate well, enjoyed lunch", "Finished all vegetables", "Tried new food today"],
            "nap": ["Slept peacefully for 2 hours", "Took a short nap", "Rested well"],
            "play": ["Played with blocks", "Had fun with friends", "Enjoyed outdoor toys"],
            "learning": ["Practiced ABCs", "Counted to 10", "Learned colors"],
            "outdoor": ["Played on swings", "Ran around playground", "Explored nature"],
            "art": ["Painted a beautiful picture", "Made a craft", "Drew with crayons"]
        }

        staff_user = users_dict[UserRole.STAFF]
        today = datetime.now().date()

        for child in children_list:
            # Create 3-5 activities for today
            num_activities = random.randint(3, 5)
            for i in range(num_activities):
                activity_type = random.choice(activity_types)
                # Random time today between 8 AM and 5 PM
                hour = random.randint(8, 16)
                minute = random.choice([0, 15, 30, 45])
                activity_time = datetime.combine(today, datetime.min.time().replace(hour=hour, minute=minute))

                activity = Activity(
                    child_id=child.id,
                    daycare_id=demo_daycare.id,
                    staff_id=staff_user.id,
                    activity_type=activity_type,
                    activity_time=activity_time,
                    duration_minutes=random.choice([15, 30, 45, 60, 90, 120]) if activity_type in ["nap", "play"] else None,
                    notes=random.choice(activity_notes[activity_type]),
                    mood=random.choice(moods)
                )
                db.add(activity)

        db.commit()
        # Silently seed without print statements (for production)


if __name__ == "__main__":
    from app.database import init_db
    init_db()
    seed_demo_data()
