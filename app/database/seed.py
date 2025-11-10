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

        # Create demo photos for children - ACTUAL DAYCARE ACTIVITY PHOTOS
        # Using realistic daycare activity photos from Unsplash (child-safe, activity-focused)

        # Specific daycare activity photos (children playing, learning, eating, etc.)
        daycare_photo_urls = {
            "playing": [
                "https://images.unsplash.com/photo-1587616211892-7e11a1f0ec19?w=400&h=300&fit=crop",  # Kids with building blocks
                "https://images.unsplash.com/photo-1503454537195-1dcabb73ffb9?w=400&h=300&fit=crop",  # Child playing with toys
                "https://images.unsplash.com/photo-1612036782180-6f0b6cd846fe?w=400&h=300&fit=crop",  # Kids playing together
            ],
            "lunch": [
                "https://images.unsplash.com/photo-1609220136736-443140cffec6?w=400&h=300&fit=crop",  # Child eating
                "https://images.unsplash.com/photo-1519340241574-2cec6aef0c01?w=400&h=300&fit=crop",  # Meal time
                "https://images.unsplash.com/photo-1490818387583-1baba5e638af?w=400&h=300&fit=crop",  # Kids eating lunch
            ],
            "art": [
                "https://images.unsplash.com/photo-1513542789411-b6a5d4f31634?w=400&h=300&fit=crop",  # Child painting
                "https://images.unsplash.com/photo-1596464716127-f2a82984de30?w=400&h=300&fit=crop",  # Art class
                "https://images.unsplash.com/photo-1515488764276-beab7607c1e6?w=400&h=300&fit=crop",  # Kids doing crafts
            ],
            "learning": [
                "https://images.unsplash.com/photo-1503676260728-1c00da094a0b?w=400&h=300&fit=crop",  # Child reading
                "https://images.unsplash.com/photo-1577896851231-70ef18881754?w=400&h=300&fit=crop",  # Kids learning
                "https://images.unsplash.com/photo-1516627145497-ae6968895b74?w=400&h=300&fit=crop",  # Classroom activity
            ],
            "outdoor": [
                "https://images.unsplash.com/photo-1560421683-6856ea585c78?w=400&h=300&fit=crop",  # Kids playing outside
                "https://images.unsplash.com/photo-1503249023995-51b0f3778ccf?w=400&h=300&fit=crop",  # Outdoor play
                "https://images.unsplash.com/photo-1599687267812-35c05ff70ee9?w=400&h=300&fit=crop",  # Playground
            ],
            "nap": [
                "https://images.unsplash.com/photo-1515488042361-ee00e0ddd4e4?w=400&h=300&fit=crop",  # Child resting
                "https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?w=400&h=300&fit=crop",  # Nap time
                "https://images.unsplash.com/photo-1519548410711-1d0d1853c2e0?w=400&h=300&fit=crop",  # Sleeping child
            ]
        }

        # Map photo activities to actual activity types
        activity_mapping = {
            "Playing": "playing",
            "Lunch Time": "lunch",
            "Nap Time": "nap",
            "Art Class": "art",
            "Outdoor Play": "outdoor",
            "Story Time": "learning",
            "Music Class": "playing",
            "Learning": "learning"
        }

        for i, child in enumerate(children_list):
            # Create 3-4 photos per child with REAL activities
            num_photos = random.randint(3, 4)
            for j in range(num_photos):
                days_ago = random.randint(0, 3)  # Recent photos only

                # Select specific activity and matching photo
                activity_names = list(activity_mapping.keys())
                selected_activity = activity_names[j % len(activity_names)]
                activity_category = activity_mapping[selected_activity]

                # Get appropriate photo for this activity
                photo_url = random.choice(daycare_photo_urls[activity_category])
                caption = f"{child.first_name} - {selected_activity}"

                photo = Photo(
                    file_name=f"{child.first_name.lower()}_{activity_category}_{j+1}.jpg",
                    original_file_name=f"{child.first_name}_{selected_activity}_{j+1}.jpg",
                    url=photo_url,
                    thumbnail_url=photo_url,  # Same URL, Unsplash handles resizing
                    caption=caption,
                    captured_at=datetime.utcnow() - timedelta(days=days_ago, hours=random.randint(8, 16)),
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
