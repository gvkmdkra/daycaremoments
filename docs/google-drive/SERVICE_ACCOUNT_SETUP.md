# 🚀 Service Account Setup Guide

## Overview

This guide will help you set up Google Drive with Service Account authentication for **production deployment**. This approach allows centralized storage management without requiring each user to authenticate.

---

## Why Service Account?

✅ **Pros:**
- No user authentication needed - staff just upload photos
- Centralized storage management
- Professional SaaS experience
- You control all data, backups, and compliance
- Include storage in your subscription pricing
- Easier support and troubleshooting

❌ **OAuth (current setup) issues:**
- Each daycare needs to authenticate with Google
- Complex onboarding
- Token management headaches
- Support complications

---

## Step 1: Create Service Account

### 1.1 Go to Google Cloud Console

1. Visit [https://console.cloud.google.com/](https://console.cloud.google.com/)
2. Select your existing "daycaremoments" project (or create new one)

### 1.2 Enable Google Drive API

1. Navigate to **APIs & Services** → **Library**
2. Search for "Google Drive API"
3. Click **Enable**

### 1.3 Create Service Account

1. Navigate to **IAM & Admin** → **Service Accounts**
2. Click **+ CREATE SERVICE ACCOUNT**
3. Fill in details:
   - **Service account name**: `daycaremoments-storage`
   - **Service account ID**: `daycaremoments-storage`
   - **Description**: `Service account for daycare photo storage`
4. Click **CREATE AND CONTINUE**
5. **Grant this service account access to project** (Optional - Skip this step)
6. Click **CONTINUE**
7. Click **DONE**

### 1.4 Create Key (Download JSON)

1. Click on the service account you just created
2. Go to **KEYS** tab
3. Click **ADD KEY** → **Create new key**
4. Choose **JSON** format
5. Click **CREATE**
6. Key file downloads automatically (e.g., `daycaremoments-xxxxx.json`)

### 1.5 Rename and Place Key File

```bash
# Rename the downloaded file
mv daycaremoments-xxxxx.json service_account.json

# Move to project root
mv service_account.json c:/Users/Mani_Moon/reapdat/code_integration/Daycare/daycaremoments/
```

---

## Step 2: Create Google Drive Folder Structure

### 2.1 Create Root Folder in YOUR Google Drive

1. Go to [https://drive.google.com](https://drive.google.com)
2. Create a new folder: **"DaycareMoments Storage"**
3. This will be the root folder for ALL daycares

### 2.2 Share Folder with Service Account

1. Right-click on **"DaycareMoments Storage"** folder
2. Click **Share**
3. Add the service account email (from `service_account.json`):
   - Open `service_account.json`
   - Copy the `client_email` value (e.g., `daycaremoments-storage@daycaremoments.iam.gserviceaccount.com`)
4. Paste into Share dialog
5. Grant **Editor** access
6. Click **Share**

### 2.3 Get Folder ID

1. Open the **"DaycareMoments Storage"** folder in Drive
2. Copy the ID from the URL:
   ```
   https://drive.google.com/drive/folders/1AbCdEfGhIjKlMnOpQrStUvWxYz
                                          ↑ This is the folder ID
   ```
3. Save this ID - you'll need it for `.env`

---

## Step 3: Configure Environment Variables

Update your `.env` file:

```bash
# -----------------------------------------------------------------------------
# Google Drive Configuration
# -----------------------------------------------------------------------------
# Set mode to 'service_account' for production
GOOGLE_DRIVE_MODE=service_account

# For OAuth mode (development/testing) - keep for reference
GOOGLE_DRIVE_CREDENTIALS=credentials.json
GOOGLE_DRIVE_FOLDER_ID=12_Vu_wuEVxAk4Fub8EnHbxR_2IZx0wns

# For Service Account mode (production) - ADD THESE
GOOGLE_DRIVE_SERVICE_ACCOUNT=service_account.json
GOOGLE_DRIVE_ROOT_FOLDER_ID=1AbCdEfGhIjKlMnOpQrStUvWxYz  # YOUR ROOT FOLDER ID
```

---

## Step 4: Test the Setup

### 4.1 Create Test Script

Create `test_service_account.py`:

```python
"""Test Service Account Google Drive connection"""
import os
from dotenv import load_dotenv
from app.services.google_drive import get_google_drive_service

load_dotenv()

def test_service_account():
    print("="*60)
    print(" SERVICE ACCOUNT TEST")
    print("="*60)

    # Initialize service
    print("\n1. Initializing service...")
    service = get_google_drive_service(mode='service_account')
    print("[OK] Service initialized")

    # Authenticate
    print("\n2. Authenticating with service account...")
    try:
        service.authenticate()
        print("[OK] Authentication successful - no browser needed!")
    except Exception as e:
        print(f"[FAIL] Authentication failed: {e}")
        return False

    # Test root folder access
    root_folder_id = os.getenv('GOOGLE_DRIVE_ROOT_FOLDER_ID')
    print(f"\n3. Testing root folder access: {root_folder_id}")

    try:
        files = service.list_files(folder_id=root_folder_id, page_size=10)
        print(f"[OK] Root folder accessible - Found {len(files)} items")
    except Exception as e:
        print(f"[FAIL] Folder access failed: {e}")
        return False

    # Create test daycare folder
    print("\n4. Creating test daycare folder...")
    try:
        folder = service.create_daycare_folder(
            daycare_id=999,
            daycare_name="Test Daycare"
        )
        print(f"[OK] Created folder: {folder['name']}")
        print(f"    Folder ID: {folder['id']}")
        print(f"    URL: {folder.get('webViewLink', 'N/A')}")

        # Clean up test folder
        print("\n5. Cleaning up test folder...")
        service.delete_file(folder['id'])
        print("[OK] Test folder deleted")

    except Exception as e:
        print(f"[FAIL] Folder creation failed: {e}")
        return False

    print("\n" + "="*60)
    print(" [SUCCESS] ALL TESTS PASSED")
    print("="*60)
    print("\nService account is working correctly!")
    print("Ready for production deployment.")

    return True

if __name__ == "__main__":
    success = test_service_account()
    exit(0 if success else 1)
```

### 4.2 Run Test

```bash
python test_service_account.py
```

**Expected output:**
```
============================================================
 SERVICE ACCOUNT TEST
============================================================

1. Initializing service...
[OK] Service initialized

2. Authenticating with service account...
[OK] Authentication successful - no browser needed!

3. Testing root folder access: 1AbCdEfGhIjKlMnOpQrStUvWxYz
[OK] Root folder accessible - Found 0 items

4. Creating test daycare folder...
[OK] Created folder: daycare_000999_Test_Daycare
    Folder ID: 1XyZaBcDeFgHiJkLmNoPqRsTuVwXyZ
    URL: https://drive.google.com/drive/folders/1XyZaBcDeFgHiJkLmNoPqRsTuVwXyZ

5. Cleaning up test folder...
[OK] Test folder deleted

============================================================
 [SUCCESS] ALL TESTS PASSED
============================================================

Service account is working correctly!
Ready for production deployment.
```

---

## Step 5: Update Database Schema

The database has been updated with new fields for daycare folder management. You'll need to recreate the database or run a migration:

### Option 1: Recreate Database (Development)

```bash
# Backup existing data if needed
python -c "import shutil; shutil.copy('daycare.db', 'daycare.db.backup')"

# Remove old database
rm daycare.db

# Start app (will recreate database)
streamlit run app.py
```

### Option 2: Add Fields to Existing Database (Production)

```python
# add_gdrive_fields.py
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.sql import text

engine = create_engine('sqlite:///daycare.db')

with engine.connect() as conn:
    # Add new columns
    conn.execute(text("ALTER TABLE daycares ADD COLUMN google_drive_folder_id VARCHAR"))
    conn.execute(text("ALTER TABLE daycares ADD COLUMN storage_quota_mb INTEGER DEFAULT 5000"))
    conn.execute(text("ALTER TABLE daycares ADD COLUMN storage_used_mb INTEGER DEFAULT 0"))
    conn.commit()

print("Database updated successfully!")
```

```bash
python add_gdrive_fields.py
```

---

## Step 6: How It Works in Production

### When a New Daycare Signs Up:

1. **Automatic Folder Creation**:
   ```python
   # app/services/onboarding.py
   from app.services.google_drive import get_google_drive_service
   from app.database import get_db
   from app.database.models import Daycare

   def onboard_daycare(daycare_name: str):
       # Create daycare in database
       with get_db() as db:
           daycare = Daycare(name=daycare_name)
           db.add(daycare)
           db.commit()
           daycare_id = daycare.id

       # Create Google Drive folder
       service = get_google_drive_service()
       service.authenticate()  # Uses service account

       folder = service.create_daycare_folder(daycare_id, daycare_name)

       # Update database with folder ID
       with get_db() as db:
           daycare = db.query(Daycare).filter_by(id=daycare_id).first()
           daycare.google_drive_folder_id = folder['id']
           db.commit()

       return daycare
   ```

2. **Folder Structure Created**:
   ```
   DaycareMoments Storage/
   └── daycare_000001_Happy_Kids/
       ├── photos/
       ├── documents/
       └── exports/
   ```

### When Staff Upload Photos:

```python
# No authentication needed! Service account handles it
from datetime import datetime

service = get_google_drive_service()
service.authenticate()  # Automatic, no browser

# Upload photo with organization
result = service.upload_photo_for_daycare(
    daycare_id=1,
    file_content=uploaded_file,
    file_name="emma_playing.jpg",
    year_month="2025-01"  # Organizes by month
)

# Folder structure:
# daycare_000001/
# └── photos/
#     └── 2025-01/
#         └── emma_playing.jpg
```

---

## Step 7: Pricing & Storage Management

### Storage Quotas

Default quota per daycare: **5GB** (5000 MB)

### Check Usage

```python
from app.services.google_drive import get_google_drive_service

service = get_google_drive_service()
service.authenticate()

usage = service.get_storage_usage(daycare_id=1)
print(f"Used: {usage['used_mb']:.2f} MB / {usage['quota_mb']} MB")
print(f"Percent: {usage['percent_used']:.1f}%")
print(f"Available: {usage['available_mb']:.2f} MB")
```

### Pricing Tiers

```python
STORAGE_TIERS = {
    'starter': {
        'quota_mb': 5000,      # 5GB
        'price_monthly': 0      # Free
    },
    'basic': {
        'quota_mb': 20000,     # 20GB
        'price_monthly': 9.99
    },
    'pro': {
        'quota_mb': 100000,    # 100GB
        'price_monthly': 29.99
    },
    'enterprise': {
        'quota_mb': 500000,    # 500GB
        'price_monthly': 99.99
    }
}
```

---

## Security Best Practices

### 1. Protect Service Account Key

```bash
# .gitignore (already updated)
service_account.json
*.json  # Be careful with this - may be too broad
```

### 2. Folder Isolation

Each daycare can ONLY access their own folder:

```python
def verify_folder_access(daycare_id: int, folder_id: str) -> bool:
    """Ensure daycare can only access their folder"""
    with get_db() as db:
        daycare = db.query(Daycare).filter_by(id=daycare_id).first()
        return folder_id == daycare.google_drive_folder_id
```

### 3. Service Account Permissions

- ✅ Editor access to root folder only
- ❌ NOT domain-wide delegation
- ✅ Scoped to Drive API only

### 4. Environment Variables

```bash
# NEVER commit these
GOOGLE_DRIVE_SERVICE_ACCOUNT=service_account.json
GOOGLE_DRIVE_ROOT_FOLDER_ID=your_folder_id
```

---

## Troubleshooting

### Error: "Service account file not found"

**Solution:**
```bash
# Verify file exists
ls service_account.json

# Check path in .env
cat .env | grep SERVICE_ACCOUNT
```

### Error: "Folder not found" or "Permission denied"

**Solution:**
1. Check root folder ID in `.env`
2. Verify service account has Editor access:
   - Open folder in Drive
   - Click Share
   - Confirm service account email is listed

### Error: "Invalid grant"

**Solution:**
Service account key may be expired or invalid:
1. Delete old `service_account.json`
2. Create new key in Google Cloud Console
3. Download and replace

---

## Switching Between OAuth and Service Account

### For Development (OAuth)

```bash
# .env
GOOGLE_DRIVE_MODE=oauth
```

### For Production (Service Account)

```bash
# .env
GOOGLE_DRIVE_MODE=service_account
```

The app automatically uses the correct authentication method!

---

## Cost Estimation

### Google Workspace Pricing

| Plan | Storage per user | Cost/month |
|------|-----------------|------------|
| Basic | 30 GB/user | $6 |
| Business Standard | 2 TB/user | $12 |
| Business Plus | 5 TB/user | $18 |

### Example: 100 Daycares

- Average usage: 10GB per daycare
- Total: 1TB storage needed
- Google Workspace Business Standard: **$12/month**
- You charge: $10/daycare/month = **$1,000/month revenue**
- Storage cost: $12/month
- **Profit: $988/month**

### ROI

- **98.8% profit margin on storage**
- Scale indefinitely
- Include in subscription pricing

---

## Next Steps

1. ✅ Complete Step 1-3 above to get service account credentials
2. ✅ Run test script to verify setup
3. ✅ Recreate database with new fields
4. ✅ Test uploading a photo
5. ✅ Deploy to production

---

## Support

For issues:
1. Check [PRODUCTION_GOOGLE_DRIVE_ARCHITECTURE.md](docs/PRODUCTION_GOOGLE_DRIVE_ARCHITECTURE.md)
2. Review [Google Drive API docs](https://developers.google.com/drive/api/v3/about-sdk)
3. Check [Service Account docs](https://cloud.google.com/iam/docs/service-accounts)

---

**You're all set! Service account authentication is production-ready.** 🎉
