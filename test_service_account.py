"""
Test Service Account Google Drive Connection
This script verifies that service account authentication works correctly
"""

import os
from dotenv import load_dotenv

load_dotenv()

def test_service_account():
    """Test service account authentication and folder operations"""

    print("="*70)
    print("  SERVICE ACCOUNT CONNECTION TEST")
    print("="*70)
    print()

    # Check service account file
    service_account_path = os.getenv('GOOGLE_DRIVE_SERVICE_ACCOUNT', 'service_account.json')

    if not os.path.exists(service_account_path):
        print(f"[FAIL] Service account file not found: {service_account_path}")
        print()
        print("Next steps:")
        print("1. Follow SERVICE_ACCOUNT_SETUP.md to create service account")
        print("2. Download key file and save as 'service_account.json'")
        print("3. Run this test again")
        return False

    print(f"[OK] Service account file found: {service_account_path}")

    # Check root folder ID
    root_folder_id = os.getenv('GOOGLE_DRIVE_ROOT_FOLDER_ID')
    if not root_folder_id:
        print("[FAIL] GOOGLE_DRIVE_ROOT_FOLDER_ID not set in .env")
        print()
        print("Next steps:")
        print("1. Create a folder in YOUR Google Drive")
        print("2. Share it with the service account email")
        print("3. Add folder ID to .env file")
        return False

    print(f"[OK] Root folder ID configured: {root_folder_id}")
    print()

    # Initialize service
    print("1. Initializing Google Drive service...")
    try:
        from app.services.google_drive import get_google_drive_service

        service = get_google_drive_service(
            service_account_path=service_account_path,
            mode='service_account'
        )
        print("[OK] Service initialized")
    except Exception as e:
        print(f"[FAIL] Service initialization failed: {e}")
        return False

    # Authenticate
    print()
    print("2. Authenticating with service account...")
    try:
        service.authenticate()
        print("[OK] Authentication successful - NO browser needed!")
    except FileNotFoundError as e:
        print(f"[FAIL] Service account file error: {e}")
        return False
    except Exception as e:
        print(f"[FAIL] Authentication failed: {e}")
        print()
        print("Possible issues:")
        print("- Service account key is invalid")
        print("- Service account doesn't have Drive API access")
        print("- Check SERVICE_ACCOUNT_SETUP.md for troubleshooting")
        return False

    # Test root folder access
    print()
    print(f"3. Testing root folder access...")
    try:
        files = service.list_files(folder_id=root_folder_id, page_size=10)
        print(f"[OK] Root folder accessible - Found {len(files)} items")

        if files:
            print()
            print("   Existing items in root folder:")
            for i, file in enumerate(files[:5], 1):
                print(f"     {i}. {file['name']}")
    except Exception as e:
        print(f"[FAIL] Root folder access failed: {e}")
        print()
        print("Possible issues:")
        print("- Folder ID is incorrect")
        print("- Service account not shared with folder")
        print("- Folder doesn't exist")
        return False

    # Create test daycare folder
    print()
    print("4. Creating test daycare folder structure...")
    try:
        folder = service.create_daycare_folder(
            daycare_id=999,
            daycare_name="Test Daycare"
        )
        print(f"[OK] Created folder: {folder['name']}")
        print(f"     Folder ID: {folder['id']}")

        if 'webViewLink' in folder:
            print(f"     View in Drive: {folder['webViewLink']}")

        # List subfolders
        print()
        print("   Checking subfolders...")
        subfolders = service.list_files(
            folder_id=folder['id'],
            query="mimeType='application/vnd.google-apps.folder'"
        )
        print(f"[OK] Created {len(subfolders)} subfolders:")
        for subfolder in subfolders:
            print(f"     - {subfolder['name']}/")

        # Test file upload
        print()
        print("5. Testing file upload...")
        import io
        test_content = b"This is a test file from DaycareMoments service account"
        test_file = io.BytesIO(test_content)

        # Get photos subfolder
        photos_folder = next((f for f in subfolders if f['name'] == 'photos'), None)
        if photos_folder:
            upload_result = service.upload_file(
                file_content=test_file,
                file_name="test_upload.txt",
                folder_id=photos_folder['id']
            )
            print(f"[OK] Uploaded test file: {upload_result['name']}")
            print(f"     File ID: {upload_result['id']}")

            # Delete test file
            service.delete_file(upload_result['id'])
            print("[OK] Test file deleted")

        # Clean up - delete test folder
        print()
        print("6. Cleaning up test folder...")
        service.delete_file(folder['id'])
        print("[OK] Test folder deleted")

    except Exception as e:
        print(f"[FAIL] Folder creation/upload failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    # All tests passed
    print()
    print("="*70)
    print("  [SUCCESS] ALL TESTS PASSED")
    print("="*70)
    print()
    print("Service account is working correctly!")
    print()
    print("What you can do now:")
    print("1. Deploy to production with GOOGLE_DRIVE_MODE=service_account")
    print("2. Each daycare will get automatic folder creation")
    print("3. Staff can upload photos without authentication")
    print("4. You manage all storage centrally")
    print()
    print(f"Root folder: https://drive.google.com/drive/folders/{root_folder_id}")

    return True


if __name__ == "__main__":
    success = test_service_account()
    exit(0 if success else 1)
