# Production Google Drive Architecture

## Overview

For production deployment, this application uses a **Service Account** approach where:
- Platform owner manages ONE Google Drive account
- Each daycare gets an isolated folder
- No OAuth required from end users
- Centralized storage and backup management

---

## Architecture

### Storage Structure

```
Platform Google Drive/
├── daycare_prod_001/
│   ├── photos/
│   │   ├── 2025-01/
│   │   ├── 2025-02/
│   │   └── ...
│   ├── documents/
│   └── exports/
├── daycare_prod_002/
│   ├── photos/
│   ├── documents/
│   └── exports/
└── ...
```

### Database Schema

```sql
-- Add to existing Daycare table
ALTER TABLE daycares ADD COLUMN google_drive_folder_id VARCHAR(255);
ALTER TABLE daycares ADD COLUMN storage_quota_mb INTEGER DEFAULT 5000;
ALTER TABLE daycares ADD COLUMN storage_used_mb INTEGER DEFAULT 0;
```

---

## Setup Instructions

### Step 1: Create Service Account

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project (or create new)
3. Enable **Google Drive API**
4. Go to **IAM & Admin** → **Service Accounts**
5. Click **Create Service Account**
   - Name: `daycaremoments-storage`
   - Description: `Service account for daycare photo storage`
6. Click **Create and Continue**
7. Grant role: **Service Account User**
8. Click **Done**

### Step 2: Generate Key

1. Click on the service account you just created
2. Go to **Keys** tab
3. Click **Add Key** → **Create new key**
4. Choose **JSON**
5. Download the key file
6. Rename to `service_account.json`
7. Place in project root

### Step 3: Share Drive Folder

1. Create a folder in YOUR Google Drive: "DaycareMoments Storage"
2. Right-click → Share
3. Add the service account email (from service_account.json)
4. Grant **Editor** access
5. Copy the folder ID from URL

### Step 4: Update Environment

```bash
# .env
GOOGLE_DRIVE_SERVICE_ACCOUNT=service_account.json
GOOGLE_DRIVE_ROOT_FOLDER_ID=your_root_folder_id
GOOGLE_DRIVE_MODE=service_account  # or 'oauth' for dev
```

### Step 5: Update .gitignore

```
# Google Drive
credentials.json
client_secret*.json
token.json
service_account.json  # Add this
```

---

## Code Implementation

### Updated Service Class

```python
# app/services/google_drive.py

class GoogleDriveService:
    def __init__(self, credentials_path=None, token_path=None, service_account_path=None):
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.service_account_path = service_account_path or os.getenv('GOOGLE_DRIVE_SERVICE_ACCOUNT')
        self.creds = None
        self.service = None

        # Determine mode
        self.mode = os.getenv('GOOGLE_DRIVE_MODE', 'oauth')

    def authenticate_service_account(self) -> bool:
        """Authenticate using service account (production mode)"""
        if not os.path.exists(self.service_account_path):
            raise FileNotFoundError(f"Service account file not found: {self.service_account_path}")

        try:
            from google.oauth2 import service_account

            SCOPES = ['https://www.googleapis.com/auth/drive']

            credentials = service_account.Credentials.from_service_account_file(
                self.service_account_path,
                scopes=SCOPES
            )

            self.creds = credentials
            self.service = build('drive', 'v3', credentials=credentials)
            return True

        except Exception as e:
            raise RuntimeError(f"Service account authentication failed: {e}")

    def authenticate(self) -> bool:
        """Smart authentication - chooses method based on mode"""
        if self.mode == 'service_account':
            return self.authenticate_service_account()
        else:
            return self.authenticate_user()

    def create_daycare_folder(self, daycare_id: int, daycare_name: str) -> Dict:
        """Create isolated folder for a daycare"""
        root_folder_id = os.getenv('GOOGLE_DRIVE_ROOT_FOLDER_ID')

        # Create main daycare folder
        folder_name = f"daycare_{daycare_id:06d}_{daycare_name.replace(' ', '_')}"

        daycare_folder = self.create_folder(
            folder_name=folder_name,
            parent_folder_id=root_folder_id
        )

        # Create subfolders
        self.create_folder('photos', parent_folder_id=daycare_folder['id'])
        self.create_folder('documents', parent_folder_id=daycare_folder['id'])
        self.create_folder('exports', parent_folder_id=daycare_folder['id'])

        return daycare_folder

    def upload_photo_for_daycare(
        self,
        daycare_id: int,
        file_content: BinaryIO,
        file_name: str,
        year_month: str = None
    ) -> Dict:
        """Upload photo to daycare's folder with date organization"""
        from app.database import get_db
        from app.database.models import Daycare

        # Get daycare folder ID
        with get_db() as db:
            daycare = db.query(Daycare).filter_by(id=daycare_id).first()
            if not daycare or not daycare.google_drive_folder_id:
                raise ValueError("Daycare folder not configured")

            base_folder_id = daycare.google_drive_folder_id

        # Get photos subfolder
        folders = self.list_files(
            folder_id=base_folder_id,
            query="mimeType='application/vnd.google-apps.folder' and name='photos'"
        )

        if not folders:
            photos_folder = self.create_folder('photos', parent_folder_id=base_folder_id)
            photos_folder_id = photos_folder['id']
        else:
            photos_folder_id = folders[0]['id']

        # Create year-month subfolder if needed
        if year_month:
            month_folders = self.list_files(
                folder_id=photos_folder_id,
                query=f"mimeType='application/vnd.google-apps.folder' and name='{year_month}'"
            )

            if not month_folders:
                month_folder = self.create_folder(year_month, parent_folder_id=photos_folder_id)
                target_folder_id = month_folder['id']
            else:
                target_folder_id = month_folders[0]['id']
        else:
            target_folder_id = photos_folder_id

        # Upload file
        result = self.upload_file(
            file_content=file_content,
            file_name=file_name,
            folder_id=target_folder_id
        )

        # Update storage usage
        file_size_mb = int(result.get('size', 0)) / (1024 * 1024)
        with get_db() as db:
            daycare = db.query(Daycare).filter_by(id=daycare_id).first()
            daycare.storage_used_mb += file_size_mb
            db.commit()

        return result

    def get_storage_usage(self, daycare_id: int) -> Dict:
        """Get storage statistics for a daycare"""
        from app.database import get_db
        from app.database.models import Daycare

        with get_db() as db:
            daycare = db.query(Daycare).filter_by(id=daycare_id).first()
            if not daycare:
                raise ValueError("Daycare not found")

            return {
                'used_mb': daycare.storage_used_mb,
                'quota_mb': daycare.storage_quota_mb,
                'percent_used': (daycare.storage_used_mb / daycare.storage_quota_mb * 100) if daycare.storage_quota_mb > 0 else 0,
                'available_mb': daycare.storage_quota_mb - daycare.storage_used_mb
            }
```

---

## Database Migration

```python
# migrations/add_google_drive_fields.py

from sqlalchemy import Column, String, Integer
from app.database.models import Daycare

def upgrade():
    """Add Google Drive fields to Daycare table"""
    # Add columns
    Daycare.google_drive_folder_id = Column(String(255))
    Daycare.storage_quota_mb = Column(Integer, default=5000)  # 5GB default
    Daycare.storage_used_mb = Column(Integer, default=0)

    print("Migration complete: Added Google Drive fields to Daycare table")

if __name__ == '__main__':
    upgrade()
```

---

## Onboarding Flow

### When New Daycare Signs Up:

```python
def onboard_new_daycare(daycare_id: int, daycare_name: str):
    """Initialize Google Drive storage for new daycare"""
    service = get_google_drive_service()
    service.authenticate()  # Uses service account in production

    # Create folder structure
    folder = service.create_daycare_folder(daycare_id, daycare_name)

    # Update database
    with get_db() as db:
        daycare = db.query(Daycare).filter_by(id=daycare_id).first()
        daycare.google_drive_folder_id = folder['id']
        daycare.storage_quota_mb = 5000  # 5GB starter plan
        daycare.storage_used_mb = 0
        db.commit()

    return folder
```

---

## Storage Quota Management

### Check Before Upload

```python
def check_storage_quota(daycare_id: int, file_size_mb: float) -> bool:
    """Check if daycare has enough storage quota"""
    service = get_google_drive_service()
    usage = service.get_storage_usage(daycare_id)

    if usage['available_mb'] < file_size_mb:
        raise ValueError(
            f"Storage quota exceeded. "
            f"Used: {usage['used_mb']:.2f}MB / {usage['quota_mb']:.2f}MB"
        )

    return True
```

### Pricing Tiers

```python
STORAGE_TIERS = {
    'starter': {'quota_mb': 5000, 'price_monthly': 0},      # 5GB free
    'basic': {'quota_mb': 20000, 'price_monthly': 9.99},    # 20GB
    'pro': {'quota_mb': 100000, 'price_monthly': 29.99},    # 100GB
    'enterprise': {'quota_mb': 500000, 'price_monthly': 99.99}  # 500GB
}
```

---

## Security Considerations

### 1. Folder Isolation

Ensure each daycare can ONLY access their folder:

```python
def verify_folder_access(daycare_id: int, folder_id: str) -> bool:
    """Verify folder belongs to daycare"""
    with get_db() as db:
        daycare = db.query(Daycare).filter_by(id=daycare_id).first()
        return folder_id == daycare.google_drive_folder_id or folder_id.startswith(daycare.google_drive_folder_id)
```

### 2. Service Account Permissions

- Service account should have **Editor** access ONLY to your root folder
- NOT domain-wide delegation
- Scoped to Drive API only

### 3. Encryption

```python
# Encrypt sensitive data in database
from cryptography.fernet import Fernet

def encrypt_token(token: str, key: bytes) -> str:
    f = Fernet(key)
    return f.encrypt(token.encode()).decode()
```

---

## Backup Strategy

### Daily Automated Backup

```python
def backup_all_daycares():
    """Create backup of all daycare folders"""
    service = get_google_drive_service()
    service.authenticate()

    backup_root = os.getenv('GOOGLE_DRIVE_BACKUP_FOLDER_ID')
    today = datetime.now().strftime('%Y-%m-%d')

    # Create daily backup folder
    backup_folder = service.create_folder(
        folder_name=f"backup_{today}",
        parent_folder_id=backup_root
    )

    # Copy each daycare's folder
    with get_db() as db:
        daycares = db.query(Daycare).all()
        for daycare in daycares:
            if daycare.google_drive_folder_id:
                # Copy folder (Google Drive API)
                service.copy_folder(
                    source_folder_id=daycare.google_drive_folder_id,
                    destination_folder_id=backup_folder['id']
                )
```

---

## Cost Estimation

### Google Drive Storage Pricing (as of 2025)

| Storage | Google Workspace Cost |
|---------|----------------------|
| 30 GB per user | $6/user/month (Basic) |
| 2 TB per user | $12/user/month (Business) |
| 5 TB per user | $18/user/month (Enterprise) |

### Your Pricing Model

If you have 100 daycares each using 10GB average:
- Total storage needed: 1TB
- Google Workspace cost: ~$12/month
- You charge: $10/daycare/month
- Revenue: $1,000/month
- Storage cost: $12/month
- **Profit: $988/month**

---

## Alternative: AWS S3 + Google Drive Sync

For even better economics:

```python
# Upload to S3 (primary)
# Optionally sync to Google Drive (for user convenience)

class HybridStorageService:
    def upload_photo(self, file, daycare_id):
        # Primary: Upload to S3
        s3_url = self.upload_to_s3(file, daycare_id)

        # Optional: Sync to Google Drive
        if daycare.wants_google_drive_backup:
            gdrive_url = self.upload_to_gdrive(file, daycare_id)

        return s3_url
```

**AWS S3 Pricing:**
- $0.023 per GB/month
- 1TB = $23/month (vs Google Workspace $12-18/month)
- But more control and features

---

## Monitoring

### Track Storage Usage

```python
def generate_storage_report():
    """Generate monthly storage report"""
    with get_db() as db:
        daycares = db.query(Daycare).all()

        report = []
        for daycare in daycares:
            usage = get_storage_usage(daycare.id)
            report.append({
                'daycare_name': daycare.name,
                'used_gb': usage['used_mb'] / 1024,
                'quota_gb': usage['quota_mb'] / 1024,
                'percent_used': usage['percent_used']
            })

        return pd.DataFrame(report)
```

---

## Conclusion

**Recommended for Production:**
1. ✅ Use Service Account for centralized management
2. ✅ Create isolated folders per daycare
3. ✅ Implement storage quotas and pricing tiers
4. ✅ Automate backups
5. ✅ Monitor usage and costs

**Do NOT use OAuth per user in production** - it's complex and creates support issues.

Your current OAuth implementation is perfect for **development and testing**, but switch to service account for production deployment.
