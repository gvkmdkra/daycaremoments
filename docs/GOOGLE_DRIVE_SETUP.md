

# Google Drive Integration - Complete Setup Guide

## Overview

DaycareMoments includes a fully reusable Google Drive integration module that allows staff to:
- Upload photos from their Google Drive account
- Import photos in bulk
- Browse Drive folders
- Auto-sync photos from designated folders

## Architecture

```
┌─────────────────────┐
│   Staff Gmail       │
│   Account           │
└──────────┬──────────┘
           │ OAuth2
           ▼
┌─────────────────────┐
│  Google Drive       │
│  Service Module     │
│  (Reusable)         │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  DaycareMoments     │
│  Database           │
└─────────────────────┘
```

## Features

### Core Module (`app/services/google_drive.py`)

**Reusable Google Drive Service with:**
- ✅ OAuth2 user authentication
- ✅ Service account authentication
- ✅ Upload files (from disk or memory)
- ✅ Download files
- ✅ List files with filters
- ✅ Create folders
- ✅ Share files with users
- ✅ Delete files
- ✅ Get file metadata

### UI Integration (`pages/07_📁_Google_Drive.py`)

**Staff-facing Streamlit interface:**
- 🔐 OAuth2 authentication flow
- 📤 Bulk photo import
- 📂 Folder browsing
- 👶 Child assignment
- ✅ Auto-approval options
- 📊 Quick statistics

## Setup Instructions

### Step 1: Install Dependencies

```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

Or add to `requirements.txt`:
```
google-auth>=2.23.0
google-auth-oauthlib>=1.1.0
google-auth-httplib2>=0.1.1
google-api-python-client>=2.100.0
```

### Step 2: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "**Select a project**" > "**New Project**"
3. Enter project name: `DaycareMoments`
4. Click "**Create**"

### Step 3: Enable Google Drive API

1. In Google Cloud Console, go to "**APIs & Services**" > "**Library**"
2. Search for "**Google Drive API**"
3. Click on it and press "**Enable**"

### Step 4: Configure OAuth Consent Screen

1. Go to "**APIs & Services**" > "**OAuth consent screen**"
2. Select "**External**" user type
3. Fill in required fields:
   - **App name**: DaycareMoments
   - **User support email**: Your email
   - **Developer contact**: Your email
4. Click "**Save and Continue**"
5. **Scopes**: Skip this step (click "**Save and Continue**")
6. **Test users**: Add staff email addresses who will use the integration
7. Click "**Save and Continue**"

### Step 5: Create OAuth 2.0 Credentials

1. Go to "**APIs & Services**" > "**Credentials**"
2. Click "**Create Credentials**" > "**OAuth client ID**"
3. Select application type: "**Desktop app**"
4. Name: `DaycareMoments Desktop Client`
5. Click "**Create**"
6. **Download the JSON file**
7. Save it as `credentials.json` in your project root directory

### Step 6: Configure Environment Variables

Add to your `.env` file:

```bash
# Google Drive Configuration
GOOGLE_DRIVE_CREDENTIALS=credentials.json
GOOGLE_DRIVE_FOLDER_ID=your_folder_id_here
```

### Step 7: Get Folder ID

1. Open [Google Drive](https://drive.google.com)
2. Navigate to the folder containing daycare photos
3. **Right-click** the folder > "**Get link**"
4. Copy the folder ID from the URL:
   ```
   https://drive.google.com/drive/folders/1abc123XYZ456def789
   ────────────────────────────────────────┬───────────────────
                                         This is the Folder ID
   ```
5. Paste it in the `.env` file

## Usage

### Method 1: Via Staff Dashboard (UI)

1. **Staff logs in** to DaycareMoments
2. **Navigate to "Google Drive"** page in sidebar
3. Go to **"Setup & Authentication"** tab
4. Click **"Authenticate with Google Drive"**
5. Browser opens → **Sign in with staff Gmail**
6. **Grant permissions** to DaycareMoments
7. Go to **"Upload from Drive"** tab
8. Enter **folder ID** (or browse folders)
9. **Select photos** to import
10. **Assign to child** and set status
11. Click **"Import Selected Photos"**

### Method 2: Programmatically (Python)

```python
from app.services.google_drive import get_google_drive_service
from app.database import get_db
from app.database.models import Photo, PhotoStatus

# Initialize service
service = get_google_drive_service()
service.authenticate_user()  # Opens browser for OAuth

# List photos in folder
folder_id = "1abc123XYZ456def789"
files = service.list_files(
    folder_id=folder_id,
    query="mimeType contains 'image/'",
    page_size=50
)

# Import to database
with get_db() as db:
    for file in files:
        photo = Photo(
            file_name=file['name'],
            url=file['webContentLink'],
            thumbnail_url=file['webViewLink'],
            child_id="child_uuid_here",
            daycare_id="daycare_uuid_here",
            status=PhotoStatus.PENDING
        )
        db.add(photo)
    db.commit()
```

### Method 3: Auto-Sync Service

Update `app/services/gdrive_sync.py` to use the new module:

```python
from app.services.google_drive import get_google_drive_service

service = get_google_drive_service()
service.authenticate_user()

# Monitor folder for new files
files = service.list_files(
    folder_id=folder_id,
    query=f"mimeType contains 'image/' and modifiedTime > '{yesterday}'"
)

for file in files:
    # Process new photos
    ...
```

## Module API Reference

### `GoogleDriveService` Class

#### Authentication Methods

```python
service.authenticate_user()
# Opens browser for OAuth2 user authentication
# Saves token for future use

service.authenticate_service_account()
# Uses service account for app-wide access
# No user interaction required
```

#### Upload Methods

```python
service.upload_file(
    file_path='photo.jpg',           # Path to local file
    file_name='custom_name.jpg',     # Optional custom name
    mime_type='image/jpeg',          # Auto-detected if not provided
    folder_id='folder_id_here',      # Upload to specific folder
    description='Photo description'  # Optional description
)
# Returns: {'id': '...', 'name': '...', 'webViewLink': '...', ...}

service.upload_file(
    file_content=BytesIO(...),       # Upload from memory
    file_name='photo.jpg',
    mime_type='image/jpeg'
)
```

#### Download Methods

```python
content = service.download_file(
    file_id='file_id_here',
    destination_path='downloaded.jpg'  # Optional, downloads to memory if not provided
)
# Returns: bytes
```

#### List Methods

```python
files = service.list_files(
    folder_id='folder_id_here',      # Optional
    query="mimeType contains 'image/'",  # Optional filter
    page_size=100,                    # Results per page
    order_by='modifiedTime desc'     # Sort order
)
# Returns: [{'id': '...', 'name': '...', ...}, ...]
```

#### Folder Methods

```python
folder = service.create_folder(
    folder_name='Daycare Photos',
    parent_folder_id='parent_id'  # Optional
)
# Returns: {'id': '...', 'name': '...', 'webViewLink': '...'}
```

#### Sharing Methods

```python
permission = service.share_file(
    file_id='file_id_here',
    email='parent@example.com',
    role='reader'  # 'reader', 'writer', 'commenter', 'owner'
)
# Returns: {'id': '...'}
```

## Security Best Practices

### OAuth2 Token Storage

- Tokens are stored in `token.json` (gitignored)
- Each staff member has their own token
- Tokens auto-refresh when expired
- Revoke access anytime from [Google Account Settings](https://myaccount.google.com/permissions)

### Credentials Protection

```bash
# .gitignore should include:
credentials.json
token.json
*.json  # Don't commit service account keys
```

### Folder Permissions

1. Create a dedicated "Daycare Photos" folder in Drive
2. Share it with all staff who need access
3. Use folder ID in environment variables
4. Staff can only access files in this folder (with `drive.file` scope)

## Troubleshooting

### Error: "Credentials file not found"

**Solution**: Ensure `credentials.json` is in project root

```bash
ls -la credentials.json  # Should exist
```

### Error: "Access denied" during OAuth

**Solution**: Add your email to test users

1. Google Cloud Console > OAuth consent screen
2. Add test users section
3. Add staff email addresses

### Error: "Token has been expired or revoked"

**Solution**: Delete token and re-authenticate

```bash
rm token.json
# Then re-run authentication in app
```

### Photos not importing

**Solution**: Check folder permissions and ID

```python
# Test folder access
service = get_google_drive_service()
service.authenticate_user()
files = service.list_files(folder_id='your_folder_id')
print(f"Found {len(files)} files")
```

## Advanced Features

### Batch Upload

```python
import os

for filename in os.listdir('./photos/'):
    if filename.endswith('.jpg'):
        service.upload_file(
            file_path=f'./photos/{filename}',
            folder_id=folder_id
        )
```

### Scheduled Auto-Import

```python
import schedule
import time

def auto_import_photos():
    service = get_google_drive_service()
    service.authenticate_user()

    # Get new photos
    yesterday = (datetime.utcnow() - timedelta(days=1)).isoformat()
    files = service.list_files(
        folder_id=folder_id,
        query=f"modifiedTime > '{yesterday}'"
    )

    # Import to database
    with get_db() as db:
        for file in files:
            # Create photo record
            ...

# Run every hour
schedule.every().hour.do(auto_import_photos)

while True:
    schedule.run_pending()
    time.sleep(60)
```

### Share Photos with Parents

```python
# After uploading photo
photo_file_id = result['id']

# Share with parent
service.share_file(
    file_id=photo_file_id,
    email='parent@example.com',
    role='reader'
)
```

## File Structure

```
daycaremoments/
├── app/
│   └── services/
│       ├── google_drive.py          # ⭐ Core reusable module
│       └── gdrive_sync.py           # Auto-sync service
├── pages/
│   └── 07_📁_Google_Drive.py        # Staff UI integration
├── examples/
│   └── google_drive_usage.py       # Usage examples
├── docs/
│   └── GOOGLE_DRIVE_SETUP.md       # This file
├── credentials.json                # OAuth2 credentials (gitignored)
├── token.json                      # User token (gitignored)
└── .env                            # Environment config
```

## Production Deployment

### For Multiple Daycares

Each daycare should have:
1. Their own Google Drive folder
2. Unique folder ID in database
3. Staff authenticate with their own accounts

### Service Account (Optional)

For server-side automation without user interaction:

1. Create service account in Google Cloud
2. Download service account JSON
3. Share Drive folder with service account email
4. Use `authenticate_service_account()` instead

### Performance Optimization

- Cache folder listings (TTL: 5 minutes)
- Use batch operations for multiple uploads
- Implement retry logic for failed uploads
- Monitor API quota usage

## Support

For issues or questions:
- Check [Google Drive API Docs](https://developers.google.com/drive/api/v3/about-sdk)
- Review [OAuth2 Guide](https://developers.google.com/identity/protocols/oauth2)
- See [examples/google_drive_usage.py](../examples/google_drive_usage.py)

---

**Last Updated**: November 10, 2025
