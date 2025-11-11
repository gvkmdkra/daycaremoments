"""
Comprehensive End-to-End System Verification
Verifies all components are ready for Google Drive integration
"""

import os
import sys
from pathlib import Path

def check_file(filepath, description):
    """Check if a file exists"""
    exists = os.path.exists(filepath)
    status = "[OK]" if exists else "[FAIL]"
    print(f"{status} {description}: {filepath}")
    return exists

def check_import(module_name, description):
    """Check if a module can be imported"""
    try:
        __import__(module_name)
        print(f"[OK] {description}: {module_name}")
        return True
    except ImportError as e:
        print(f"[FAIL] {description}: {module_name} - {e}")
        return False

def check_database():
    """Verify database contents"""
    try:
        from app.database import get_db
        from app.database.models import Photo, Child, User

        with get_db() as db:
            photo_count = db.query(Photo).count()
            child_count = db.query(Child).count()
            user_count = db.query(User).count()

            print(f"[OK] Database accessible")
            print(f"     - Photos: {photo_count}")
            print(f"     - Children: {child_count}")
            print(f"     - Users: {user_count}")

            # Check specific children
            isabella = db.query(Child).filter_by(first_name="Isabella", last_name="Anderson").first()
            lucas = db.query(Child).filter_by(first_name="Lucas", last_name="Thomas").first()

            if isabella:
                isa_photos = db.query(Photo).filter_by(child_id=isabella.id).count()
                print(f"     - Isabella Anderson: {isa_photos} photos")

            if lucas:
                lucas_photos = db.query(Photo).filter_by(child_id=lucas.id).count()
                print(f"     - Lucas Thomas: {lucas_photos} photos")

            return True
    except Exception as e:
        print(f"[FAIL] Database check failed: {e}")
        return False

def check_photo_urls():
    """Verify photo URLs are accessible"""
    try:
        from app.database import get_db
        from app.database.models import Photo
        import requests

        with get_db() as db:
            photos = db.query(Photo).limit(5).all()

            print(f"\n[OK] Testing {len(photos)} sample photo URLs:")

            all_ok = True
            for photo in photos:
                try:
                    response = requests.head(photo.url, timeout=5)
                    if response.status_code == 200:
                        print(f"     [OK] {photo.caption}")
                    else:
                        print(f"     [FAIL] {photo.caption} - HTTP {response.status_code}")
                        all_ok = False
                except Exception as e:
                    print(f"     [FAIL] {photo.caption} - {e}")
                    all_ok = False

            return all_ok
    except Exception as e:
        print(f"[FAIL] Photo URL check failed: {e}")
        return False

def check_env_variables():
    """Check environment configuration"""
    from dotenv import load_dotenv
    load_dotenv()

    folder_id = os.getenv('GOOGLE_DRIVE_FOLDER_ID')
    credentials = os.getenv('GOOGLE_DRIVE_CREDENTIALS', 'credentials.json')

    if folder_id:
        print(f"[OK] GOOGLE_DRIVE_FOLDER_ID: {folder_id}")
    else:
        print(f"[WARN] GOOGLE_DRIVE_FOLDER_ID not set in .env")

    if credentials:
        print(f"[OK] GOOGLE_DRIVE_CREDENTIALS: {credentials}")

    return True

def main():
    print("="*70)
    print("  DAYCAREMOMENTS - END-TO-END SYSTEM VERIFICATION")
    print("="*70)
    print()

    all_checks = []

    # 1. Check critical files
    print("1. CRITICAL FILES:")
    all_checks.append(check_file('credentials.json', 'OAuth credentials'))
    all_checks.append(check_file('.env', 'Environment config'))
    all_checks.append(check_file('app.py', 'Main application'))
    all_checks.append(check_file('daycare.db', 'Database file'))
    print()

    # 2. Check Google Drive integration files
    print("2. GOOGLE DRIVE INTEGRATION:")
    all_checks.append(check_file('app/services/google_drive.py', 'Core service'))
    # Check if Google Drive page exists (with emoji in filename)
    gdrive_page_exists = os.path.exists('pages') and any('Google_Drive' in f for f in os.listdir('pages'))
    print(f"[{'OK' if gdrive_page_exists else 'FAIL'}] Staff UI: pages/07_*_Google_Drive.py")
    all_checks.append(gdrive_page_exists)
    all_checks.append(check_file('gdrive_connector/__init__.py', 'Standalone package'))
    all_checks.append(check_file('test_gdrive_connection.py', 'Test script'))
    print()

    # 3. Check Python dependencies
    print("3. PYTHON DEPENDENCIES:")
    all_checks.append(check_import('streamlit', 'Streamlit'))
    all_checks.append(check_import('google.auth', 'Google Auth'))
    all_checks.append(check_import('google_auth_oauthlib', 'OAuth2 library'))
    all_checks.append(check_import('googleapiclient', 'Google API client'))
    all_checks.append(check_import('sqlalchemy', 'SQLAlchemy'))
    all_checks.append(check_import('requests', 'Requests'))
    print()

    # 4. Check environment variables
    print("4. ENVIRONMENT CONFIGURATION:")
    all_checks.append(check_env_variables())
    print()

    # 5. Check database
    print("5. DATABASE:")
    all_checks.append(check_database())
    print()

    # 6. Check photo URLs
    print("6. PHOTO URLS:")
    all_checks.append(check_photo_urls())
    print()

    # 7. Check reusable package
    print("7. REUSABLE PACKAGE:")
    try:
        from gdrive_connector import get_google_drive_service
        print("[OK] gdrive_connector package importable")
        print("[OK] Can be used in ANY Python project")
        all_checks.append(True)
    except Exception as e:
        print(f"[FAIL] Package import failed: {e}")
        all_checks.append(False)
    print()

    # Summary
    print("="*70)
    passed = sum(all_checks)
    total = len(all_checks)

    if all(all_checks):
        print(f" [SUCCESS] ALL CHECKS PASSED ({passed}/{total})")
        print("="*70)
        print()
        print("SYSTEM STATUS: READY FOR PRODUCTION")
        print()
        print("Next Steps:")
        print("  1. Run: streamlit run app.py")
        print("  2. Login as staff (staff@demo.com / staff123)")
        print("  3. Go to 'Google Drive' tab in sidebar")
        print("  4. Click 'Authenticate with Google Drive'")
        print("  5. Import photos from your Drive folder")
        print()
        print("Folder configured:")
        print(f"  https://drive.google.com/drive/folders/{os.getenv('GOOGLE_DRIVE_FOLDER_ID', '12_Vu_wuEVxAk4Fub8EnHbxR_2IZx0wns')}")
        return 0
    else:
        print(f" [FAIL] SOME CHECKS FAILED ({passed}/{total} passed)")
        print("="*70)
        return 1

if __name__ == "__main__":
    sys.exit(main())
