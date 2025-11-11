# 📁 Google Drive Connector - Standalone Reusable Package

**A drop-in Google Drive integration for any Python project**

## Features

✅ OAuth2 user authentication
✅ Service account support
✅ Upload/download files
✅ List & filter files
✅ Create folders
✅ Share files
✅ Delete files
✅ Zero configuration required

## Installation

### Step 1: Copy Package to Your Project

```bash
# Copy the entire gdrive_connector folder to your project
cp -r gdrive_connector /path/to/your/project/
```

### Step 2: Install Dependencies

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

### Step 3: Get Google Cloud Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project
3. Enable **Google Drive API**
4. Create **OAuth 2.0 credentials**
5. Download `credentials.json`
6. Place it in your project root

## Quick Start

### Basic Usage

```python
from gdrive_connector import get_google_drive_service

# Initialize
service = get_google_drive_service()

# Authenticate (opens browser)
service.authenticate_user()

# Upload a file
result = service.upload_file(
    file_path='photo.jpg',
    folder_id='your_folder_id'  # Optional
)
print(f"Uploaded: {result['name']}")
print(f"URL: {result['webViewLink']}")

# List files
files = service.list_files(
    folder_id='your_folder_id',
    query="mimeType contains 'image/'",
    page_size=50
)

for file in files:
    print(f"- {file['name']}")

# Download a file
content = service.download_file(
    file_id='file_id_here',
    destination_path='downloaded.jpg'
)
```

### Upload from Memory

```python
import io
from PIL import Image

# Create image in memory
img = Image.new('RGB', (400, 300), color='blue')
img_bytes = io.BytesIO()
img.save(img_bytes, format='PNG')
img_bytes.seek(0)

# Upload
result = service.upload_file(
    file_content=img_bytes,
    file_name='generated_image.png',
    mime_type='image/png',
    folder_id='your_folder_id'
)
```

### Batch Upload

```python
import os

folder_id = "your_folder_id"

for filename in os.listdir('./photos/'):
    if filename.endswith(('.jpg', '.png')):
        result = service.upload_file(
            file_path=f'./photos/{filename}',
            folder_id=folder_id
        )
        print(f"✓ Uploaded: {filename}")
```

### Create Folder

```python
folder = service.create_folder(
    folder_name='My Photos 2025',
    parent_folder_id='parent_id'  # Optional
)
print(f"Created folder: {folder['name']}")
print(f"Folder ID: {folder['id']}")
```

### Share File

```python
# Share with specific user
service.share_file(
    file_id='your_file_id',
    email='user@example.com',
    role='reader'  # 'reader', 'writer', 'commenter', 'owner'
)
```

## API Reference

### Authentication

```python
# User authentication (OAuth2)
service.authenticate_user()

# Service account (no user interaction)
service.authenticate_service_account()
```

### Upload Methods

```python
service.upload_file(
    file_path=str,              # Path to local file
    file_content=BinaryIO,      # Or file-like object
    file_name=str,              # Custom name
    mime_type=str,              # Auto-detected if not provided
    folder_id=str,              # Upload to folder
    description=str             # File description
) -> Dict
# Returns: {'id', 'name', 'webViewLink', 'webContentLink', ...}
```

### Download Methods

```python
content = service.download_file(
    file_id=str,                # Google Drive file ID
    destination_path=str        # Optional local path
) -> bytes
```

### List Methods

```python
files = service.list_files(
    folder_id=str,              # Optional folder ID
    query=str,                  # Drive API query
    page_size=int,              # Results per page (max 1000)
    order_by=str                # Sort order
) -> List[Dict]
```

**Query Examples:**
```python
# Images only
query="mimeType contains 'image/'"

# Modified after date
query="modifiedTime > '2025-01-01T00:00:00'"

# Name contains
query="name contains 'daycare'"

# Combine filters
query="mimeType='image/jpeg' and name contains 'emma'"
```

### Folder Methods

```python
folder = service.create_folder(
    folder_name=str,
    parent_folder_id=str        # Optional
) -> Dict
```

### Sharing Methods

```python
permission = service.share_file(
    file_id=str,
    email=str,
    role=str                    # 'reader', 'writer', 'commenter', 'owner'
) -> Dict
```

### Metadata Methods

```python
metadata = service.get_file_metadata(file_id=str) -> Dict
```

### Delete Methods

```python
success = service.delete_file(file_id=str) -> bool
```

## Configuration

### Environment Variables (Optional)

Create `.env` file:

```bash
GOOGLE_DRIVE_CREDENTIALS=credentials.json
GOOGLE_DRIVE_FOLDER_ID=your_default_folder_id
```

Load in code:

```python
import os
from dotenv import load_dotenv

load_dotenv()

service = get_google_drive_service(
    credentials_path=os.getenv('GOOGLE_DRIVE_CREDENTIALS'),
    token_path='token.json'
)
```

### Custom Credentials Path

```python
service = get_google_drive_service(
    credentials_path='/path/to/credentials.json',
    token_path='/path/to/token.json'
)
```

## Use Cases

### 1. Photo Backup System

```python
def backup_photos(local_dir, drive_folder_id):
    service = get_google_drive_service()
    service.authenticate_user()

    for file in os.listdir(local_dir):
        if file.endswith(('.jpg', '.png')):
            service.upload_file(
                file_path=os.path.join(local_dir, file),
                folder_id=drive_folder_id
            )
```

### 2. Auto-Sync with Database

```python
from sqlalchemy import create_engine, Column, String
from sqlalchemy.orm import declarative_base, Session

Base = declarative_base()

class Photo(Base):
    __tablename__ = 'photos'
    id = Column(String, primary_key=True)
    name = Column(String)
    drive_url = Column(String)

def sync_to_database():
    service = get_google_drive_service()
    service.authenticate_user()

    files = service.list_files(
        folder_id='your_folder_id',
        query="mimeType contains 'image/'"
    )

    engine = create_engine('sqlite:///photos.db')
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        for file in files:
            photo = Photo(
                id=file['id'],
                name=file['name'],
                drive_url=file['webViewLink']
            )
            session.merge(photo)
        session.commit()
```

### 3. Flask/FastAPI Integration

```python
from flask import Flask, request, jsonify
from gdrive_connector import get_google_drive_service

app = Flask(__name__)
service = get_google_drive_service()
service.authenticate_user()

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']

    result = service.upload_file(
        file_content=file.stream,
        file_name=file.filename,
        mime_type=file.content_type,
        folder_id=request.form.get('folder_id')
    )

    return jsonify(result)

@app.route('/files')
def list_files():
    folder_id = request.args.get('folder_id')
    files = service.list_files(folder_id=folder_id)
    return jsonify(files)
```

### 4. Scheduled Auto-Import

```python
import schedule
import time
from datetime import datetime, timedelta

def auto_import():
    service = get_google_drive_service()
    service.authenticate_user()

    # Get files from last hour
    one_hour_ago = (datetime.utcnow() - timedelta(hours=1)).isoformat() + 'Z'

    files = service.list_files(
        folder_id='your_folder_id',
        query=f"modifiedTime > '{one_hour_ago}'"
    )

    print(f"Found {len(files)} new files")
    # Process files...

# Run every hour
schedule.every().hour.do(auto_import)

while True:
    schedule.run_pending()
    time.sleep(60)
```

## Error Handling

```python
try:
    service = get_google_drive_service()
    service.authenticate_user()

    result = service.upload_file(
        file_path='photo.jpg',
        folder_id='invalid_folder_id'
    )
except FileNotFoundError:
    print("Credentials file not found")
except RuntimeError as e:
    print(f"Upload failed: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Security Best Practices

### 1. Protect Credentials

```bash
# Add to .gitignore
credentials.json
token.json
*.json  # If using service accounts
```

### 2. Use Limited Scopes

The package uses these scopes by default:
- `https://www.googleapis.com/auth/drive.file` - Access only to files created by app
- `https://www.googleapis.com/auth/drive` - Full drive access (use with caution)

Modify in `google_drive_service.py` if needed:

```python
SCOPES = ['https://www.googleapis.com/auth/drive.file']  # Most restrictive
```

### 3. Service Account for Automation

For server-side automation without user interaction:

```python
service.authenticate_service_account()
```

### 4. Revoke Access

Users can revoke access anytime:
[Google Account Permissions](https://myaccount.google.com/permissions)

## Troubleshooting

### Issue: "Credentials file not found"

**Solution:**
```bash
# Verify file exists
ls credentials.json

# Check path
service = get_google_drive_service(
    credentials_path='./path/to/credentials.json'
)
```

### Issue: "Access denied"

**Solution:** Add test users in OAuth consent screen (Google Cloud Console)

### Issue: "Token expired"

**Solution:** Delete token and re-authenticate
```bash
rm token.json
# Re-run authentication
```

### Issue: "Quota exceeded"

**Solution:** Check API quotas in Google Cloud Console

## Testing

```python
# Test connection
def test_connection():
    service = get_google_drive_service()
    service.authenticate_user()

    # Create test folder
    folder = service.create_folder('Test Folder')
    print(f"✓ Folder created: {folder['id']}")

    # Upload test file
    with open('test.txt', 'w') as f:
        f.write('Test content')

    result = service.upload_file(
        file_path='test.txt',
        folder_id=folder['id']
    )
    print(f"✓ File uploaded: {result['id']}")

    # List files
    files = service.list_files(folder_id=folder['id'])
    print(f"✓ Files found: {len(files)}")

    # Clean up
    service.delete_file(result['id'])
    service.delete_file(folder['id'])
    print("✓ Cleanup complete")

if __name__ == '__main__':
    test_connection()
```

## License

MIT License - Use freely in any project, commercial or personal.

## Support

For issues or questions, refer to:
- [Google Drive API Docs](https://developers.google.com/drive/api/v3/about-sdk)
- [OAuth2 Guide](https://developers.google.com/identity/protocols/oauth2)

---

**Created for DaycareMoments** - A reusable package for Google Drive integration in any Python project.
