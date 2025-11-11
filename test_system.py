"""
Comprehensive System Testing Script
Tests all components to ensure working application
"""

import requests
import sys
from app.database import init_db, get_db
from app.database.models import Photo, Child, Activity, User
from app.database.seed import seed_demo_data

def test_image_urls():
    """Test that image URLs are accessible"""
    print("\n" + "="*60)
    print("TESTING IMAGE URL ACCESSIBILITY")
    print("="*60)

    test_urls = [
        "https://placehold.co/400x300/87CEEB/000000/png?text=Child+Playing",
        "https://placehold.co/400x300/FFE4B5/000000/png?text=Lunch+Time",
        "https://placehold.co/400x300/E6E6FA/000000/png?text=Nap+Time",
    ]

    all_passed = True
    for url in test_urls:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✓ PASS: {url[:60]}...")
            else:
                print(f"✗ FAIL: {url} - Status {response.status_code}")
                all_passed = False
        except Exception as e:
            print(f"✗ FAIL: {url} - {str(e)}")
            all_passed = False

    return all_passed

def test_database():
    """Test database initialization and data"""
    print("\n" + "="*60)
    print("TESTING DATABASE")
    print("="*60)

    try:
        # Initialize database
        init_db()
        print("✓ Database initialized")

        # Seed data
        seed_demo_data()
        print("✓ Demo data seeded")

        # Verify data
        with get_db() as db:
            user_count = db.query(User).count()
            child_count = db.query(Child).count()
            photo_count = db.query(Photo).count()
            activity_count = db.query(Activity).count()

            print(f"\nDatabase Contents:")
            print(f"  Users: {user_count}")
            print(f"  Children: {child_count}")
            print(f"  Photos: {photo_count}")
            print(f"  Activities: {activity_count}")

            # Test sample photos
            sample_photos = db.query(Photo).limit(5).all()
            print(f"\nSample Photo URLs:")
            for photo in sample_photos:
                child = db.query(Child).filter(Child.id == photo.child_id).first()
                print(f"  - {child.first_name}: {photo.caption}")
                print(f"    URL: {photo.url[:80]}...")

                # Verify URL is accessible
                try:
                    resp = requests.head(photo.url, timeout=5)
                    if resp.status_code == 200:
                        print(f"    ✓ URL accessible")
                    else:
                        print(f"    ✗ URL returns {resp.status_code}")
                except Exception as e:
                    print(f"    ✗ URL error: {str(e)}")

            # Test Isabella and Lucas specifically
            print(f"\nSpecific Child Verification:")
            for child_name in ["Isabella", "Lucas"]:
                child = db.query(Child).filter(Child.first_name == child_name).first()
                if child:
                    photos = db.query(Photo).filter(Photo.child_id == child.id).all()
                    print(f"  {child_name} {child.last_name}: {len(photos)} photos")
                    for p in photos:
                        print(f"    - {p.caption}")

        return True
    except Exception as e:
        print(f"✗ Database test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_authentication():
    """Test login credentials"""
    print("\n" + "="*60)
    print("TESTING AUTHENTICATION")
    print("="*60)

    from app.utils.auth import verify_password, get_user_by_email

    test_credentials = [
        ("admin@demo.com", "admin123", "Admin"),
        ("staff@demo.com", "staff123", "Staff"),
        ("parent@demo.com", "parent123", "Parent"),
    ]

    all_passed = True
    with get_db() as db:
        for email, password, role in test_credentials:
            user = get_user_by_email(email, db)
            if user and verify_password(password, user.password_hash):
                print(f"✓ {role} login works: {email}")
            else:
                print(f"✗ {role} login FAILED: {email}")
                all_passed = False

    return all_passed

def run_all_tests():
    """Run comprehensive system tests"""
    print("\n" + "="*80)
    print(" DAYCAREMOMENTS - COMPREHENSIVE SYSTEM TEST")
    print("="*80)

    results = {
        "Image URLs": test_image_urls(),
        "Database": test_database(),
        "Authentication": test_authentication(),
    }

    print("\n" + "="*80)
    print(" TEST SUMMARY")
    print("="*80)

    all_passed = True
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{test_name:.<40} {status}")
        if not passed:
            all_passed = False

    print("\n" + "="*80)
    if all_passed:
        print(" ALL TESTS PASSED - SYSTEM READY")
        print("="*80)
        print("\nAccess the app at: http://localhost:8501")
        print("\nDemo Credentials:")
        print("  Admin:  admin@demo.com / admin123")
        print("  Staff:  staff@demo.com / staff123")
        print("  Parent: parent@demo.com / parent123")
        return 0
    else:
        print(" SOME TESTS FAILED - ISSUES NEED FIXING")
        print("="*80)
        return 1

if __name__ == "__main__":
    sys.exit(run_all_tests())
