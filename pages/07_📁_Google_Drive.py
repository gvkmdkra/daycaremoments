"""Google Drive Integration - Staff Upload & Import"""

import streamlit as st
from app.utils.auth import require_auth, get_current_user
from app.database import get_db
from app.database.models import Photo, Child, PhotoStatus
from app.services.google_drive import get_google_drive_service, GOOGLE_DRIVE_AVAILABLE
from app.config import Config
from datetime import datetime
import uuid
import os
from app.utils.ui_theme import apply_professional_theme

st.set_page_config(page_title="Google Drive Integration", page_icon="📁", layout="wide")

# Apply professional theme
apply_professional_theme()

# Require authentication (staff and admin only)
require_auth(['staff', 'admin'])
user = get_current_user()

st.title("📁 Google Drive Integration")
st.write("Upload photos from your Google Drive to DaycareMoments")

# Check if Google Drive is available
if not GOOGLE_DRIVE_AVAILABLE:
    st.error("❌ Google Drive integration not available")
    st.info("""
    To enable Google Drive integration, install required packages:
    ```bash
    pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
    ```
    """)
    st.stop()

# Initialize session state
if 'gdrive_authenticated' not in st.session_state:
    st.session_state.gdrive_authenticated = False
if 'gdrive_service' not in st.session_state:
    st.session_state.gdrive_service = None
if 'selected_folder_id' not in st.session_state:
    st.session_state.selected_folder_id = None

# Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "🔐 Setup & Authentication",
    "📤 Upload from Drive",
    "📂 Browse Drive",
    "ℹ️ How to Setup"
])

# ===== TAB 1: SETUP & AUTHENTICATION =====
with tab1:
    st.subheader("🔐 Google Drive Authentication")

    # Check credentials
    credentials_path = Config.GOOGLE_DRIVE_CREDENTIALS or 'credentials.json'
    token_path = 'token.json'

    if not os.path.exists(credentials_path):
        st.warning(f"⚠️ Credentials file not found: {credentials_path}")
        st.markdown("""
        ### Setup Required

        1. **Create Google Cloud Project**:
           - Go to [Google Cloud Console](https://console.cloud.google.com/)
           - Create a new project or select existing one

        2. **Enable Google Drive API**:
           - Navigate to "APIs & Services" > "Library"
           - Search for "Google Drive API"
           - Click "Enable"

        3. **Create OAuth 2.0 Credentials**:
           - Go to "APIs & Services" > "Credentials"
           - Click "Create Credentials" > "OAuth client ID"
           - Select "Desktop app" as application type
           - Download the JSON file
           - Save it as `credentials.json` in your project root

        4. **Add to .env file**:
           ```
           GOOGLE_DRIVE_CREDENTIALS=credentials.json
           ```
        """)

        # File uploader for credentials
        st.markdown("### Or Upload Credentials File")
        uploaded_creds = st.file_uploader(
            "Upload credentials.json",
            type=['json'],
            help="Download from Google Cloud Console"
        )

        if uploaded_creds:
            with open(credentials_path, 'wb') as f:
                f.write(uploaded_creds.getvalue())
            st.success(f"✅ Credentials saved to {credentials_path}")
            st.rerun()

    else:
        st.success(f"✅ Credentials file found: {credentials_path}")

        # Authentication status
        if st.session_state.gdrive_authenticated:
            st.success("✅ Authenticated with Google Drive")

            col1, col2 = st.columns(2)
            with col1:
                st.info(f"**User:** {user.email}")
            with col2:
                if st.button("🔓 Logout from Google Drive"):
                    st.session_state.gdrive_authenticated = False
                    st.session_state.gdrive_service = None
                    if os.path.exists(token_path):
                        os.remove(token_path)
                    st.success("Logged out successfully")
                    st.rerun()

        else:
            st.info("🔒 Not authenticated. Click below to connect your Google Drive")

            if st.button("🔐 Authenticate with Google Drive", use_container_width=True):
                try:
                    with st.spinner("Opening browser for authentication..."):
                        service = get_google_drive_service(credentials_path, token_path)
                        service.authenticate_user()

                        st.session_state.gdrive_service = service
                        st.session_state.gdrive_authenticated = True

                        st.success("✅ Successfully authenticated!")
                        st.rerun()

                except Exception as e:
                    st.error(f"❌ Authentication failed: {str(e)}")

# ===== TAB 2: UPLOAD FROM DRIVE =====
with tab2:
    st.subheader("📤 Upload Photos from Google Drive")

    if not st.session_state.gdrive_authenticated:
        st.warning("⚠️ Please authenticate with Google Drive first (see Setup tab)")
    else:
        service = st.session_state.gdrive_service

        # Folder selection
        st.markdown("### Select Drive Folder")
        folder_id_input = st.text_input(
            "Google Drive Folder ID",
            value=Config.GOOGLE_DRIVE_FOLDER_ID or "",
            help="Right-click folder in Drive > Get link > Copy the ID from the URL"
        )

        if folder_id_input:
            st.session_state.selected_folder_id = folder_id_input

        if st.button("📂 Load Photos from Folder"):
            if not st.session_state.selected_folder_id:
                st.error("Please enter a folder ID")
            else:
                try:
                    with st.spinner("Loading photos from Google Drive..."):
                        # List image files in folder
                        files = service.list_files(
                            folder_id=st.session_state.selected_folder_id,
                            query="mimeType contains 'image/'",
                            page_size=50
                        )

                        if not files:
                            st.info("No images found in this folder")
                        else:
                            st.success(f"Found {len(files)} image(s)")

                            # Store files in session state
                            st.session_state.drive_files = files

                except Exception as e:
                    st.error(f"❌ Error loading folder: {str(e)}")

        # Display found files
        if 'drive_files' in st.session_state and st.session_state.drive_files:
            st.markdown("### Photos Found in Drive")

            # Get children for selection
            with get_db() as db:
                children = db.query(Child).filter(
                    Child.daycare_id == user.daycare_id,
                    Child.is_active == True
                ).all()

                child_options = {f"{c.first_name} {c.last_name}": c.id for c in children}

            # Import settings
            col1, col2 = st.columns(2)
            with col1:
                selected_child_name = st.selectbox(
                    "Assign photos to child:",
                    options=list(child_options.keys()),
                    help="All imported photos will be tagged to this child"
                )
                selected_child_id = child_options[selected_child_name]

            with col2:
                import_status = st.selectbox(
                    "Photo status:",
                    options=["Pending Review", "Auto-Approve"],
                    help="Pending requires admin approval"
                )
                photo_status = PhotoStatus.PENDING if import_status == "Pending Review" else PhotoStatus.APPROVED

            # Display files with checkboxes
            st.markdown("### Select Photos to Import")
            selected_files = []

            for idx, file in enumerate(st.session_state.drive_files):
                col1, col2, col3 = st.columns([1, 4, 2])

                with col1:
                    selected = st.checkbox(
                        "Select",
                        key=f"select_{file['id']}",
                        value=True
                    )

                with col2:
                    st.text(f"📄 {file['name']}")
                    st.caption(f"Modified: {file.get('modifiedTime', 'Unknown')}")

                with col3:
                    size_mb = int(file.get('size', 0)) / (1024 * 1024)
                    st.caption(f"Size: {size_mb:.2f} MB")

                if selected:
                    selected_files.append(file)

            st.divider()

            # Import button
            if st.button(f"📥 Import {len(selected_files)} Selected Photo(s)", use_container_width=True):
                if not selected_files:
                    st.warning("No photos selected")
                else:
                    progress_bar = st.progress(0)
                    status_text = st.empty()

                    imported_count = 0

                    with get_db() as db:
                        for idx, file in enumerate(selected_files):
                            try:
                                status_text.text(f"Importing {idx + 1}/{len(selected_files)}: {file['name']}")

                                # Create photo record
                                photo = Photo(
                                    file_name=file['name'],
                                    original_file_name=file['name'],
                                    url=file.get('webContentLink', file.get('webViewLink', '')),
                                    thumbnail_url=file.get('webViewLink', ''),
                                    caption=f"{selected_child_name} - Imported from Google Drive",
                                    captured_at=datetime.fromisoformat(file['modifiedTime'].replace('Z', '+00:00')),
                                    uploaded_by=user.id,
                                    child_id=selected_child_id,
                                    daycare_id=user.daycare_id,
                                    status=photo_status,
                                    approved_by=user.id if photo_status == PhotoStatus.APPROVED else None
                                )

                                db.add(photo)
                                imported_count += 1

                            except Exception as e:
                                st.warning(f"Failed to import {file['name']}: {str(e)}")

                            progress_bar.progress((idx + 1) / len(selected_files))

                        db.commit()

                    status_text.empty()
                    progress_bar.empty()
                    st.success(f"✅ Successfully imported {imported_count} photo(s)!")

                    # Clear files
                    del st.session_state.drive_files

# ===== TAB 3: BROWSE DRIVE =====
with tab3:
    st.subheader("📂 Browse Google Drive")

    if not st.session_state.gdrive_authenticated:
        st.warning("⚠️ Please authenticate with Google Drive first")
    else:
        service = st.session_state.gdrive_service

        if st.button("🔄 List All Folders", use_container_width=True):
            try:
                with st.spinner("Loading folders..."):
                    folders = service.list_files(
                        query="mimeType='application/vnd.google-apps.folder'",
                        page_size=50,
                        order_by='modifiedTime desc'
                    )

                    if folders:
                        st.success(f"Found {len(folders)} folder(s)")

                        for folder in folders:
                            col1, col2 = st.columns([3, 1])

                            with col1:
                                st.markdown(f"**📁 {folder['name']}**")
                                st.caption(f"ID: `{folder['id']}`")

                            with col2:
                                if st.button("Use This", key=f"use_{folder['id']}"):
                                    st.session_state.selected_folder_id = folder['id']
                                    st.success(f"Selected: {folder['name']}")

                            st.divider()
                    else:
                        st.info("No folders found")

            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

# ===== TAB 4: HOW TO SETUP =====
with tab4:
    st.subheader("ℹ️ How to Setup Google Drive Integration")

    st.markdown("""
    ## Complete Setup Guide

    ### Step 1: Create Google Cloud Project

    1. Go to [Google Cloud Console](https://console.cloud.google.com/)
    2. Click "Select a project" > "New Project"
    3. Enter project name: "DaycareMoments"
    4. Click "Create"

    ### Step 2: Enable Google Drive API

    1. In Google Cloud Console, go to "APIs & Services" > "Library"
    2. Search for "Google Drive API"
    3. Click on it and press "Enable"

    ### Step 3: Create OAuth 2.0 Credentials

    1. Go to "APIs & Services" > "Credentials"
    2. Click "Create Credentials" > "OAuth client ID"
    3. If prompted, configure the OAuth consent screen:
       - User Type: External
       - App name: DaycareMoments
       - User support email: Your email
       - Developer contact: Your email
    4. Back to Create OAuth client ID:
       - Application type: "Desktop app"
       - Name: "DaycareMoments Desktop"
    5. Click "Create"
    6. Download the JSON file
    7. Save it as `credentials.json` in your project root

    ### Step 4: Configure Application

    Add to your `.env` file:
    ```
    GOOGLE_DRIVE_CREDENTIALS=credentials.json
    GOOGLE_DRIVE_FOLDER_ID=your_folder_id_here
    ```

    ### Step 5: Get Folder ID

    1. Open Google Drive in your browser
    2. Navigate to the folder containing daycare photos
    3. Right-click the folder > "Get link"
    4. Copy the ID from the URL:
       ```
       https://drive.google.com/drive/folders/FOLDER_ID_HERE
       ```
    5. Paste the folder ID in the Upload tab

    ### Step 6: Authenticate

    1. Go to "Setup & Authentication" tab
    2. Click "Authenticate with Google Drive"
    3. Browser will open - sign in with your Gmail account
    4. Grant permissions to DaycareMoments
    5. You're ready to import photos!

    ### Security Notes

    - Each staff member authenticates with their own Google account
    - Only files in the specified folder are accessible
    - Photos are imported as database references (not stored locally)
    - You can revoke access anytime from Google Account settings

    ### Supported File Types

    - JPG/JPEG
    - PNG
    - GIF
    - WebP
    - HEIC (converted automatically)

    ### Troubleshooting

    **Error: "Credentials file not found"**
    - Ensure `credentials.json` is in the project root directory

    **Error: "Access denied"**
    - Check OAuth consent screen configuration
    - Add your email to test users if app is in testing mode

    **Photos not appearing**
    - Verify folder ID is correct
    - Ensure folder contains image files
    - Check file permissions (should be accessible to authenticated user)
    """)

st.divider()

# Quick Stats
with st.expander("📊 Quick Stats"):
    with get_db() as db:
        from app.database.models import Photo
        total_photos = db.query(Photo).filter(Photo.daycare_id == user.daycare_id).count()
        pending_photos = db.query(Photo).filter(
            Photo.daycare_id == user.daycare_id,
            Photo.status == PhotoStatus.PENDING
        ).count()

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Photos", total_photos)
        with col2:
            st.metric("Pending Review", pending_photos)
        with col3:
            st.metric("Drive Status", "✅ Connected" if st.session_state.gdrive_authenticated else "❌ Not Connected")
