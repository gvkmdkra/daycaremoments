"""
Example usage of Google Drive Service
Demonstrates all features of the reusable Google Drive module
"""

from app.services.google_drive import get_google_drive_service
import os

# Example 1: User Authentication (OAuth2)
def example_user_authentication():
    """Authenticate with user's Google account"""
    print("=== Example 1: User Authentication ===")

    service = get_google_drive_service(
        credentials_path='credentials.json',
        token_path='token.json'
    )

    # This will open browser for user to grant permissions
    service.authenticate_user()

    print("✅ Authenticated successfully!")


# Example 2: Upload File from Disk
def example_upload_from_disk():
    """Upload a local file to Google Drive"""
    print("\n=== Example 2: Upload File from Disk ===")

    service = get_google_drive_service()
    service.authenticate_user()

    # Upload photo to root folder
    result = service.upload_file(
        file_path='sample_photo.jpg',
        description='Daycare photo - Emma playing'
    )

    print(f"✅ Uploaded: {result['name']}")
    print(f"   File ID: {result['id']}")
    print(f"   View: {result['webViewLink']}")


# Example 3: Upload to Specific Folder
def example_upload_to_folder():
    """Upload file to a specific Google Drive folder"""
    print("\n=== Example 3: Upload to Folder ===")

    service = get_google_drive_service()
    service.authenticate_user()

    folder_id = "1234567890abcdefg"  # Your folder ID

    result = service.upload_file(
        file_path='daycare_photo.jpg',
        folder_id=folder_id,
        description='Uploaded from DaycareMoments'
    )

    print(f"✅ Uploaded to folder: {result['name']}")


# Example 4: Upload from Memory (BytesIO)
def example_upload_from_memory():
    """Upload file from memory (useful for camera uploads)"""
    print("\n=== Example 4: Upload from Memory ===")
    import io
    from PIL import Image

    service = get_google_drive_service()
    service.authenticate_user()

    # Create an image in memory
    img = Image.new('RGB', (400, 300), color='lightblue')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)

    result = service.upload_file(
        file_content=img_bytes,
        file_name='generated_photo.png',
        mime_type='image/png'
    )

    print(f"✅ Uploaded from memory: {result['name']}")


# Example 5: List Files in Folder
def example_list_files():
    """List all files in a specific folder"""
    print("\n=== Example 5: List Files ===")

    service = get_google_drive_service()
    service.authenticate_user()

    folder_id = "1234567890abcdefg"

    # List all images in folder
    files = service.list_files(
        folder_id=folder_id,
        query="mimeType contains 'image/'",
        page_size=20
    )

    print(f"Found {len(files)} image(s):")
    for file in files:
        print(f"  - {file['name']} ({file['size']} bytes)")


# Example 6: Download File
def example_download_file():
    """Download a file from Google Drive"""
    print("\n=== Example 6: Download File ===")

    service = get_google_drive_service()
    service.authenticate_user()

    file_id = "1234567890abcdefg"

    # Download to disk
    content = service.download_file(
        file_id=file_id,
        destination_path='downloaded_photo.jpg'
    )

    print(f"✅ Downloaded {len(content)} bytes")


# Example 7: Create Folder
def example_create_folder():
    """Create a new folder in Google Drive"""
    print("\n=== Example 7: Create Folder ===")

    service = get_google_drive_service()
    service.authenticate_user()

    folder = service.create_folder(
        folder_name='Daycare Photos - November 2025'
    )

    print(f"✅ Created folder: {folder['name']}")
    print(f"   Folder ID: {folder['id']}")


# Example 8: Share File with User
def example_share_file():
    """Share a file with specific user"""
    print("\n=== Example 8: Share File ===")

    service = get_google_drive_service()
    service.authenticate_user()

    file_id = "1234567890abcdefg"
    parent_email = "parent@example.com"

    permission = service.share_file(
        file_id=file_id,
        email=parent_email,
        role='reader'  # Can view but not edit
    )

    print(f"✅ Shared with {parent_email}")


# Example 9: Batch Upload Multiple Photos
def example_batch_upload():
    """Upload multiple photos at once"""
    print("\n=== Example 9: Batch Upload ===")

    service = get_google_drive_service()
    service.authenticate_user()

    folder_id = "1234567890abcdefg"
    photo_dir = './daycare_photos/'

    uploaded_files = []

    for filename in os.listdir(photo_dir):
        if filename.endswith(('.jpg', '.png', '.jpeg')):
            file_path = os.path.join(photo_dir, filename)

            result = service.upload_file(
                file_path=file_path,
                folder_id=folder_id
            )

            uploaded_files.append(result)
            print(f"✅ Uploaded: {filename}")

    print(f"\nTotal uploaded: {len(uploaded_files)} files")


# Example 10: Integrate with Database
def example_database_integration():
    """Upload to Drive and save to database"""
    print("\n=== Example 10: Database Integration ===")

    from app.database import get_db
    from app.database.models import Photo, PhotoStatus

    service = get_google_drive_service()
    service.authenticate_user()

    folder_id = "1234567890abcdefg"

    # Upload to Drive
    result = service.upload_file(
        file_path='emma_playing.jpg',
        folder_id=folder_id
    )

    # Save to database
    with get_db() as db:
        photo = Photo(
            file_name=result['name'],
            original_file_name=result['name'],
            url=result['webContentLink'],
            thumbnail_url=result['webViewLink'],
            caption="Emma playing with blocks",
            child_id="child_id_here",
            daycare_id="daycare_id_here",
            uploaded_by="staff_id_here",
            status=PhotoStatus.APPROVED
        )
        db.add(photo)
        db.commit()

    print(f"✅ Uploaded to Drive and saved to database")


# Example 11: Auto-Import from Drive Folder
def example_auto_import():
    """Automatically import new photos from Drive folder"""
    print("\n=== Example 11: Auto-Import ===")

    from app.database import get_db
    from app.database.models import Photo, PhotoStatus
    from datetime import datetime, timedelta

    service = get_google_drive_service()
    service.authenticate_user()

    folder_id = "1234567890abcdefg"

    # Get photos uploaded in last 24 hours
    yesterday = (datetime.utcnow() - timedelta(days=1)).isoformat() + 'Z'

    files = service.list_files(
        folder_id=folder_id,
        query=f"mimeType contains 'image/' and modifiedTime > '{yesterday}'"
    )

    print(f"Found {len(files)} new photo(s)")

    with get_db() as db:
        for file in files:
            # Check if already imported
            existing = db.query(Photo).filter(
                Photo.original_file_name == file['name']
            ).first()

            if not existing:
                photo = Photo(
                    file_name=file['name'],
                    original_file_name=file['name'],
                    url=file['webContentLink'],
                    thumbnail_url=file['webViewLink'],
                    caption="Auto-imported from Google Drive",
                    # ... other fields
                    status=PhotoStatus.PENDING
                )
                db.add(photo)
                print(f"  ✅ Imported: {file['name']}")

        db.commit()


if __name__ == "__main__":
    print("Google Drive Service Examples")
    print("=" * 60)

    # Run examples (uncomment as needed)
    # example_user_authentication()
    # example_upload_from_disk()
    # example_upload_to_folder()
    # example_upload_from_memory()
    # example_list_files()
    # example_download_file()
    # example_create_folder()
    # example_share_file()
    # example_batch_upload()
    # example_database_integration()
    # example_auto_import()

    print("\n" + "=" * 60)
    print("Examples completed!")
