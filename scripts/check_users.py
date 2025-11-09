"""Check users in database"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import get_db
from app.database.models import User
from app.utils.auth import verify_password

print("Checking users in database...")
print("=" * 60)

with get_db() as db:
    users = db.query(User).all()

    if not users:
        print("❌ NO USERS FOUND!")
        print("Run: python scripts/quick_seed.py")
    else:
        print(f"✅ Found {len(users)} users:\n")

        for user in users:
            print(f"Email: {user.email}")
            print(f"Name: {user.first_name} {user.last_name}")
            print(f"Role: {user.role.value}")

            # Test password
            if user.email == "parent@demo.com":
                test_pass = verify_password("parent123", user.password_hash)
                print(f"Password 'parent123' works: {test_pass}")

            print("-" * 60)

print("\n✅ Demo credentials:")
print("admin@demo.com / admin123")
print("staff@demo.com / staff123")
print("parent@demo.com / parent123")
