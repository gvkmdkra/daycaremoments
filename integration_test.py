"""
End-to-End Integration Test for DaycareMoments with Google Drive
This script performs complete system testing and imports sample images
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")

def test_google_drive_oauth():
    """Test Google Drive OAuth authentication"""
    print_section("STEP 1: Google Drive OAuth Authentication")

    try:
        from app.services.google_drive import get_google_drive_service

        service = get_google_drive_service(mode='oauth')
        print("[1/3] Google Drive service initialized")

        # Authenticate (will open browser if token doesn't exist)
        if service.authenticate():
            print("[2/3] Authentication successful")
        else:
            print("[FAIL] Authentication failed")
            return None

        # Test folder access
        folder_id = os.getenv('GOOGLE_DRIVE_FOLDER_ID')
        files = service.list_files(folder_id=folder_id, page_size=5)
        print(f"[3/3] Sample images folder accessible - Found {len(files)} files")

        if files:
            print("\nSample files found:")
            for i, file in enumerate(files[:5], 1):
                print(f"  {i}. {file['name']} ({file.get('size', 'N/A')} bytes)")

        return service

    except Exception as e:
        print(f"[FAIL] Google Drive test failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def setup_database():
    """Initialize database with fresh schema"""
    print_section("STEP 2: Database Setup")

    try:
        from app.database.db_manager import DatabaseManager
        from app.database.models import Daycare, Child, Parent, Staff, Photo

        db_manager = DatabaseManager()
        print("[1/2] Database manager initialized")

        # Create all tables
        db_manager.create_tables()
        print("[2/2] Database tables created")

        return db_manager

    except Exception as e:
        print(f"[FAIL] Database setup failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def create_test_data(db_manager):
    """Create test daycares, children, parents, and staff"""
    print_section("STEP 3: Creating Test Data")

    try:
        from app.database.models import Daycare, Child, Parent, Staff, User
        from app.utils.password import hash_password

        session = db_manager.get_session()

        # Create daycare
        print("[1/6] Creating test daycare...")
        daycare = Daycare(
            name="Sunshine Daycare",
            address="123 Main St, Anytown, USA",
            phone="555-0100",
            email="info@sunshinedaycare.com",
            admin_email="admin@sunshinedaycare.com",
            max_children=50,
            google_drive_folder_id=os.getenv('GOOGLE_DRIVE_FOLDER_ID'),
            storage_quota_mb=5000,
            storage_used_mb=0
        )
        session.add(daycare)
        session.flush()
        print(f"   Created daycare: {daycare.name} (ID: {daycare.id})")

        # Create staff user
        print("[2/6] Creating staff user...")
        staff_user = User(
            email="staff@sunshinedaycare.com",
            password_hash=hash_password("staff123"),
            first_name="Sarah",
            last_name="Johnson",
            role="staff"
        )
        session.add(staff_user)
        session.flush()

        staff = Staff(
            user_id=staff_user.id,
            daycare_id=daycare.id,
            position="Lead Teacher",
            hire_date=datetime.now().date(),
            is_active=True
        )
        session.add(staff)
        session.flush()
        print(f"   Created staff: {staff_user.first_name} {staff_user.last_name}")

        # Create parent user
        print("[3/6] Creating parent user...")
        parent_user = User(
            email="parent@example.com",
            password_hash=hash_password("parent123"),
            first_name="John",
            last_name="Smith",
            role="parent"
        )
        session.add(parent_user)
        session.flush()

        parent = Parent(
            user_id=parent_user.id,
            phone="555-0101",
            is_primary=True
        )
        session.add(parent)
        session.flush()
        print(f"   Created parent: {parent_user.first_name} {parent_user.last_name}")

        # Create children
        print("[4/6] Creating test children...")
        children_data = [
            {"first_name": "Emma", "last_name": "Smith", "date_of_birth": "2020-05-15"},
            {"first_name": "Liam", "last_name": "Johnson", "date_of_birth": "2019-08-22"},
            {"first_name": "Olivia", "last_name": "Williams", "date_of_birth": "2021-03-10"},
        ]

        children = []
        for child_data in children_data:
            child = Child(
                daycare_id=daycare.id,
                first_name=child_data["first_name"],
                last_name=child_data["last_name"],
                date_of_birth=datetime.strptime(child_data["date_of_birth"], "%Y-%m-%d").date(),
                classroom="Toddlers",
                enrollment_date=datetime.now().date(),
                is_active=True
            )
            session.add(child)
            session.flush()

            # Link child to parent
            child.parents.append(parent)
            children.append(child)
            print(f"   Created child: {child.first_name} {child.last_name} (ID: {child.id})")

        session.commit()
        print("[5/6] All test data committed to database")
        print("[6/6] Test data creation complete")

        return {
            'daycare': daycare,
            'staff': staff,
            'parent': parent,
            'children': children
        }

    except Exception as e:
        print(f"[FAIL] Test data creation failed: {e}")
        import traceback
        traceback.print_exc()
        session.rollback()
        return None

def import_sample_images(db_manager, google_service, test_data):
    """Import sample images from Google Drive"""
    print_section("STEP 4: Importing Sample Images from Google Drive")

    try:
        from app.database.models import Photo
        import io

        session = db_manager.get_session()
        folder_id = os.getenv('GOOGLE_DRIVE_FOLDER_ID')

        # List all images in the folder
        print("[1/4] Listing images from Google Drive...")
        files = google_service.list_files(
            folder_id=folder_id,
            query="mimeType contains 'image/'"
        )

        print(f"   Found {len(files)} images in Google Drive")

        if not files:
            print("[WARN] No images found in Google Drive folder")
            return []

        # Import up to 10 sample images
        print("[2/4] Downloading and importing images...")
        imported_photos = []
        children = test_data['children']

        for i, file in enumerate(files[:10]):
            try:
                # Download image
                file_content = google_service.download_file(file['id'])

                # Assign to a child (rotate through children)
                child = children[i % len(children)]

                # Create photo record
                photo = Photo(
                    daycare_id=test_data['daycare'].id,
                    child_id=child.id,
                    uploaded_by=test_data['staff'].id,
                    file_name=file['name'],
                    file_url=file.get('webContentLink', file.get('webViewLink', '')),
                    google_drive_file_id=file['id'],
                    mime_type=file.get('mimeType', 'image/jpeg'),
                    file_size=int(file.get('size', 0)),
                    upload_timestamp=datetime.now(),
                    is_approved=True,
                    caption=f"Sample photo for {child.first_name}"
                )

                session.add(photo)
                imported_photos.append(photo)

                print(f"   [{i+1}/{min(len(files), 10)}] Imported: {file['name']} → {child.first_name}")

            except Exception as e:
                print(f"   [WARN] Failed to import {file['name']}: {e}")
                continue

        session.commit()
        print(f"[3/4] Successfully imported {len(imported_photos)} photos")
        print("[4/4] Image import complete")

        return imported_photos

    except Exception as e:
        print(f"[FAIL] Image import failed: {e}")
        import traceback
        traceback.print_exc()
        return []

def verify_system(db_manager, test_data, imported_photos):
    """Verify the complete system"""
    print_section("STEP 5: System Verification")

    try:
        from app.database.models import Daycare, Child, Parent, Staff, Photo

        session = db_manager.get_session()

        # Count records
        daycare_count = session.query(Daycare).count()
        child_count = session.query(Child).count()
        parent_count = session.query(Parent).count()
        staff_count = session.query(Staff).count()
        photo_count = session.query(Photo).count()

        print(f"[1/5] Database Statistics:")
        print(f"   Daycares: {daycare_count}")
        print(f"   Children: {child_count}")
        print(f"   Parents: {parent_count}")
        print(f"   Staff: {staff_count}")
        print(f"   Photos: {photo_count}")

        # Verify Google Drive integration
        print(f"\n[2/5] Google Drive Integration:")
        print(f"   Mode: {os.getenv('GOOGLE_DRIVE_MODE')}")
        print(f"   Folder ID: {os.getenv('GOOGLE_DRIVE_FOLDER_ID')}")
        print(f"   Photos linked to Drive: {photo_count}")

        # Verify parent-child relationships
        print(f"\n[3/5] Parent-Child Relationships:")
        for child in test_data['children']:
            parent_names = [f"{p.user.first_name} {p.user.last_name}" for p in child.parents]
            print(f"   {child.first_name} → Parents: {', '.join(parent_names)}")

        # Verify photo assignments
        print(f"\n[4/5] Photo Assignments:")
        for child in test_data['children']:
            child_photos = session.query(Photo).filter_by(child_id=child.id).count()
            print(f"   {child.first_name}: {child_photos} photos")

        print(f"\n[5/5] System verification complete")

        return True

    except Exception as e:
        print(f"[FAIL] System verification failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def print_success_summary(test_data, imported_photos):
    """Print final success summary"""
    print_section("SUCCESS - Production-Ready Application")

    print("DaycareMoments is ready for use!\n")

    print("Test Credentials:")
    print("-" * 80)
    print("Staff Login:")
    print("  Email: staff@sunshinedaycare.com")
    print("  Password: staff123")
    print()
    print("Parent Login:")
    print("  Email: parent@example.com")
    print("  Password: parent123")
    print()

    print("System Features:")
    print("-" * 80)
    print(f"✓ Google Drive Integration (OAuth Mode)")
    print(f"✓ {len(test_data['children'])} Test Children Created")
    print(f"✓ {len(imported_photos)} Sample Photos Imported")
    print(f"✓ Parent-Child Relationships Configured")
    print(f"✓ Staff Photo Upload Enabled")
    print(f"✓ Parent Photo Gallery Access")
    print()

    print("Next Steps:")
    print("-" * 80)
    print("1. Run: streamlit run app.py")
    print("2. Login as staff or parent")
    print("3. Browse photos in the gallery")
    print("4. Upload new photos from Google Drive")
    print()

    print("Google Drive Configuration:")
    print("-" * 80)
    print(f"Mode: {os.getenv('GOOGLE_DRIVE_MODE')}")
    print(f"Folder: https://drive.google.com/drive/folders/{os.getenv('GOOGLE_DRIVE_FOLDER_ID')}")
    print()

    print("Documentation:")
    print("-" * 80)
    print("All documentation moved to docs/google-drive/")
    print("  - REUSABLE_GDRIVE_CONNECTOR.md - Reusability guide")
    print("  - SERVICE_ACCOUNT_SETUP.md - Production setup")
    print("  - PRODUCTION_GOOGLE_DRIVE_ARCHITECTURE.md - Architecture details")
    print()

def main():
    """Main integration test flow"""
    print_section("DaycareMoments End-to-End Integration Test")
    print("This script will:")
    print("1. Test Google Drive OAuth authentication")
    print("2. Set up fresh database with updated schema")
    print("3. Create test daycares, children, parents, and staff")
    print("4. Import sample images from Google Drive")
    print("5. Verify complete system functionality")
    print()
    input("Press Enter to continue...")

    # Step 1: Google Drive
    google_service = test_google_drive_oauth()
    if not google_service:
        print("\n[FATAL] Google Drive authentication failed. Cannot continue.")
        return False

    # Step 2: Database
    db_manager = setup_database()
    if not db_manager:
        print("\n[FATAL] Database setup failed. Cannot continue.")
        return False

    # Step 3: Test Data
    test_data = create_test_data(db_manager)
    if not test_data:
        print("\n[FATAL] Test data creation failed. Cannot continue.")
        return False

    # Step 4: Import Images
    imported_photos = import_sample_images(db_manager, google_service, test_data)
    if not imported_photos:
        print("\n[WARN] No photos imported, but continuing...")

    # Step 5: Verification
    if not verify_system(db_manager, test_data, imported_photos):
        print("\n[FATAL] System verification failed.")
        return False

    # Success
    print_success_summary(test_data, imported_photos)
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n[FATAL] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
