# 🚀 Google Drive Integration - Quick Start

## ✅ Setup Complete!

Your Google Drive integration is **fully configured and ready to use**.

### What's Already Done

✅ OAuth credentials downloaded and renamed
✅ Folder ID extracted from your Drive URL
✅ Environment variables configured
✅ Dependencies installed
✅ Standalone reusable package created
✅ Test script ready

---

## 📋 Current Configuration

```
Credentials File: credentials.json
Folder ID: 12_Vu_wuEVxAk4Fub8EnHbxR_2IZx0wns
Folder Path: daycaremoments/sample_images
```

---

## 🎯 How to Use (3 Ways)

### 1. Via Staff Dashboard (UI - Recommended)

```bash
# 1. Start the app
streamlit run app.py

# 2. Login as staff
Email: staff@demo.com
Password: staff123

# 3. Click "📁 Google Drive" in sidebar

# 4. Go to "Setup & Authentication" tab

# 5. Click "Authenticate with Google Drive"
# Browser opens → Sign in with your Gmail

# 6. Go to "Upload from Drive" tab

# 7. Click "Load Photos from Folder"

# 8. Select photos and import!
```

### 2. Test the Connection

```bash
python test_gdrive_connection.py
```

This will:
- Verify credentials
- Authenticate with your Gmail
- List files in your Drive folder
- Show available images

### 3. Use Programmatically

```python
from gdrive_connector import get_google_drive_service

# Initialize and authenticate
service = get_google_drive_service()
service.authenticate_user()  # Opens browser

# List images in your folder
files = service.list_files(
    folder_id='12_Vu_wuEVxAk4Fub8EnHbxR_2IZx0wns',
    query="mimeType contains 'image/'",
    page_size=50
)

print(f"Found {len(files)} images")
for file in files:
    print(f"- {file['name']}")
```

---

## 📁 Package Structure

### Integrated with DaycareMoments

```
app/services/google_drive.py       # Used by the app
pages/07_📁_Google_Drive.py        # Staff UI
```

### Standalone Reusable Package

```
gdrive_connector/
├── __init__.py                   # Package entry point
├── google_drive_service.py       # Core service
└── README.md                     # Full documentation
```

**Copy `gdrive_connector/` to ANY project for instant Google Drive integration!**

---

## 🔑 First Time Setup (When You Run the App)

1. **Browser Opens Automatically**
   - Shows Google sign-in page
   - Sign in with your Gmail account

2. **Grant Permissions**
   - Click "Allow" to give DaycareMoments access
   - Permissions: Read/write Drive files

3. **Token Saved**
   - `token.json` created automatically
   - Future runs won't need authentication

4. **Ready to Import**
   - Photos from your Drive folder visible
   - Select and import with one click

---

## 📷 Your Sample Images

Location: https://drive.google.com/drive/folders/12_Vu_wuEVxAk4Fub8EnHbxR_2IZx0wns

The app is configured to access this folder automatically.

---

## 🛠️ Troubleshooting

### "Credentials file not found"

```bash
# Verify it exists
ls credentials.json

# Should see:
# credentials.json
```

### "Access denied"

**Solution:** Your OAuth app needs to add test users

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. APIs & Services → OAuth consent screen
3. Add your Gmail to "Test users"

### "Token expired"

```bash
# Delete and re-authenticate
rm token.json
python test_gdrive_connection.py
```

---

## 🌟 Features Available

### Upload Methods
- Upload from local file
- Upload from memory (BytesIO)
- Batch upload multiple files
- Upload to specific folders

### Download Methods
- Download to file
- Download to memory
- Get direct URLs

### File Operations
- List files with filters
- Search by name, type, date
- Create folders
- Share with users
- Delete files

### Smart Filters
```python
# Images only
query="mimeType contains 'image/'"

# JPEGs only
query="mimeType='image/jpeg'"

# Modified after date
query="modifiedTime > '2025-01-01T00:00:00'"

# Name contains
query="name contains 'daycare'"
```

---

## 📚 Documentation

- **Staff UI Guide**: [docs/GOOGLE_DRIVE_SETUP.md](docs/GOOGLE_DRIVE_SETUP.md)
- **Standalone Package**: [gdrive_connector/README.md](gdrive_connector/README.md)
- **Usage Examples**: [examples/google_drive_usage.py](examples/google_drive_usage.py)

---

## 🔐 Security

- ✅ Credentials never committed to Git
- ✅ Tokens stored locally (not in repo)
- ✅ OAuth2 secure authentication
- ✅ Folder-level access control
- ✅ Can revoke access anytime

---

## 🎉 You're All Set!

Your Google Drive integration is **production-ready**. You can now:

1. **Import photos** from your Drive folder into DaycareMoments
2. **Use the standalone package** in other Python projects
3. **Automate workflows** with the API

### Next Steps

```bash
# Test the connection
python test_gdrive_connection.py

# Or start the app
streamlit run app.py
```

---

**Need help?** Check the full documentation in `docs/GOOGLE_DRIVE_SETUP.md`
