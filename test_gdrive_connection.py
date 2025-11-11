"""
Test Google Drive Connection
Quick verification that credentials and folder access work
"""

import os
from gdrive_connector import get_google_drive_service

def test_connection():
    """Test Google Drive authentication and folder access"""

    print("="*60)
    print(" GOOGLE DRIVE CONNECTION TEST")
    print("="*60)

    # Check credentials file
    if not os.path.exists('credentials.json'):
        print("❌ ERROR: credentials.json not found")
        print("   Please download OAuth credentials from Google Cloud Console")
        return False

    print("✓ credentials.json found")

    # Initialize service
    print("\nInitializing Google Drive service...")
    try:
        service = get_google_drive_service(
            credentials_path='credentials.json',
            token_path='token.json'
        )
        print("✓ Service initialized")
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        return False

    # Authenticate
    print("\nAuthenticating (browser will open)...")
    try:
        service.authenticate_user()
        print("✓ Authentication successful")
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        return False

    # Test folder access
    folder_id = os.getenv('GOOGLE_DRIVE_FOLDER_ID', '12_Vu_wuEVxAk4Fub8EnHbxR_2IZx0wns')
    print(f"\nTesting folder access: {folder_id}")

    try:
        files = service.list_files(
            folder_id=folder_id,
            page_size=10
        )
        print(f"✓ Folder accessible - Found {len(files)} file(s)")

        if files:
            print("\nSample files:")
            for i, file in enumerate(files[:5], 1):
                size_kb = int(file.get('size', 0)) / 1024 if file.get('size') else 0
                print(f"  {i}. {file['name']} ({size_kb:.1f} KB)")

        # List images specifically
        images = service.list_files(
            folder_id=folder_id,
            query="mimeType contains 'image/'",
            page_size=20
        )
        print(f"\n✓ Found {len(images)} image file(s)")

        if images:
            print("\nImage files:")
            for i, img in enumerate(images[:5], 1):
                print(f"  {i}. {img['name']}")

    except Exception as e:
        print(f"❌ Folder access failed: {e}")
        return False

    # All tests passed
    print("\n" + "="*60)
    print(" ✅ ALL TESTS PASSED")
    print("="*60)
    print("\nYour Google Drive is properly connected!")
    print(f"Folder ID: {folder_id}")
    print(f"Files available: {len(files)}")
    print(f"Images available: {len(images)}")
    print("\n🎉 Ready to import photos into DaycareMoments!")

    return True


if __name__ == "__main__":
    success = test_connection()
    exit(0 if success else 1)
