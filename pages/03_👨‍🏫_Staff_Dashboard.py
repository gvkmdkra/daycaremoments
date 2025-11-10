"""Staff Dashboard - Upload photos, manage activities, approve photos"""

import streamlit as st
from app.utils.auth import require_auth, get_current_user
from app.database import get_db
from app.database.models import Child, Photo, Activity, PhotoStatus, User
from datetime import datetime, timedelta
from sqlalchemy import desc
import uuid
import random
from app.utils.ui_theme import apply_professional_theme

st.set_page_config(page_title="Staff Dashboard", page_icon="👨‍🏫", layout="wide")

# Apply professional theme
apply_professional_theme()

# Require staff or admin authentication
require_auth(['staff', 'admin'])
user = get_current_user()

st.title("👨‍🏫 Staff Dashboard")
st.write(f"Welcome, **{user.first_name}**!")

# ===== TABS =====
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📸 Upload Photos", "☁️ Google Drive", "✅ Approve Photos", "📝 Log Activity", "👶 Children"])

# ===== TAB 1: MANUAL UPLOAD WITH STUDENT SELECTION =====
with tab1:
    st.subheader("📸 Upload Photos with Student Selection")

    # Get children from the daycare
    with get_db() as db:
        children_db = db.query(Child).filter(Child.daycare_id == user.daycare_id).all()
        children = [{
            'id': c.id,
            'first_name': c.first_name,
            'last_name': c.last_name
        } for c in children_db]

    if not children:
        st.warning("No children found in your daycare. Please add children first.")
    else:
        with st.form("upload_photos_form"):
            # Student selection - MULTISELECT for multiple children
            child_names = {f"{child['first_name']} {child['last_name']}": child['id'] for child in children}
            selected_children = st.multiselect(
                "👶 Select Children in Photos",
                options=list(child_names.keys()),
                help="Select one or more children who appear in these photos"
            )

            # File uploader
            uploaded_files = st.file_uploader(
                "📷 Select Photos",
                type=['jpg', 'jpeg', 'png'],
                accept_multiple_files=True,
                help="Upload multiple photos at once (JPEG, JPG, PNG)"
            )

            # Activity selector
            activity_type = st.selectbox(
                "📋 Activity Type",
                options=["Meal", "Nap", "Play", "Learning", "Outdoor", "Art", "Other"]
            )

            # Caption
            caption = st.text_area("💬 Caption (optional)", placeholder="What's happening in these photos?")

            # Auto-approve option (staff can auto-approve)
            auto_approve = st.checkbox("✅ Auto-approve photos", value=True)

            submit = st.form_submit_button("📤 Upload Photos", use_container_width=True)

            if submit:
                if not selected_children:
                    st.error("❌ Please select at least one child before uploading")
                elif not uploaded_files:
                    st.error("❌ Please select photos to upload")
                else:
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    photos_uploaded = 0

                    for idx, uploaded_file in enumerate(uploaded_files):
                        status_text.text(f"Processing {uploaded_file.name}...")

                        # In production, upload to Google Drive, R2, or S3
                        # For demo, use placeholder URL
                        photo_url = f"https://via.placeholder.com/400x300/667eea/ffffff?text={uploaded_file.name}"

                        # Create photo for each selected child
                        with get_db() as db:
                            for child_name in selected_children:
                                child_id = child_names[child_name]

                                photo = Photo(
                                    id=str(uuid.uuid4()),
                                    file_name=uploaded_file.name,
                                    original_file_name=uploaded_file.name,
                                    url=photo_url,
                                    child_id=child_id,
                                    daycare_id=user.daycare_id,
                                    uploaded_by=user.id,
                                    caption=caption,
                                    captured_at=datetime.utcnow(),
                                    status=PhotoStatus.APPROVED if auto_approve else PhotoStatus.PENDING,
                                    approved_by=user.id if auto_approve else None
                                )
                                db.add(photo)
                                photos_uploaded += 1

                            db.commit()

                        progress_bar.progress((idx + 1) / len(uploaded_files))

                    status_text.empty()
                    st.success(f"✅ Uploaded {photos_uploaded} photos successfully for {len(selected_children)} child(ren)!")

                    if not auto_approve:
                        st.info("Photos are pending approval. Check the 'Approve Photos' tab.")

# ===== TAB 2: GOOGLE DRIVE UPLOAD =====
with tab2:
    st.subheader("☁️ Import Photos from Google Drive")

    st.info("📌 **Google Drive Integration** - Import photos directly from your Google Drive folder")

    # Get children for tagging
    with get_db() as db:
        children_db = db.query(Child).filter(Child.daycare_id == user.daycare_id).all()
        children = [{
            'id': c.id,
            'first_name': c.first_name,
            'last_name': c.last_name
        } for c in children_db]

    if not children:
        st.warning("No children found in your daycare. Please add children first.")
    else:
        with st.form("gdrive_import_form"):
            # Google Drive folder URL input
            gdrive_url = st.text_input(
                "📁 Google Drive Folder URL",
                placeholder="https://drive.google.com/drive/folders/...",
                help="Paste the shared link to your Google Drive folder containing photos"
            )

            # Student selection for all photos in folder
            child_names = {f"{child['first_name']} {child['last_name']}": child['id'] for child in children}
            selected_children = st.multiselect(
                "👶 Tag Children in These Photos",
                options=list(child_names.keys()),
                help="Select children who appear in the photos from this folder"
            )

            # Activity type
            activity_type = st.selectbox(
                "📋 Activity Type",
                options=["Meal", "Nap", "Play", "Learning", "Outdoor", "Art", "Other"]
            )

            # Caption
            caption = st.text_area("💬 Caption for All Photos", placeholder="Optional caption for all imported photos")

            auto_approve = st.checkbox("✅ Auto-approve imported photos", value=True)

            submit_gdrive = st.form_submit_button("☁️ Import from Google Drive", use_container_width=True)

            if submit_gdrive:
                if not gdrive_url:
                    st.error("❌ Please provide a Google Drive folder URL")
                elif not selected_children:
                    st.error("❌ Please select at least one child to tag")
                else:
                    # In production, this would use Google Drive API
                    # For demo, simulate importing 5-10 photos
                    st.info("🔄 Connecting to Google Drive...")

                    import time
                    time.sleep(1)

                    # Simulate photo import
                    num_photos = random.randint(5, 10)
                    st.info(f"📥 Found {num_photos} photos in folder. Importing...")

                    progress_bar = st.progress(0)
                    photos_imported = 0

                    for i in range(num_photos):
                        photo_name = f"gdrive_photo_{i+1}.jpg"
                        photo_url = f"https://via.placeholder.com/400x300/38ef7d/ffffff?text=GDrive+Photo+{i+1}"

                        with get_db() as db:
                            for child_name in selected_children:
                                child_id = child_names[child_name]

                                photo = Photo(
                                    id=str(uuid.uuid4()),
                                    file_name=photo_name,
                                    original_file_name=photo_name,
                                    url=photo_url,
                                    child_id=child_id,
                                    daycare_id=user.daycare_id,
                                    uploaded_by=user.id,
                                    caption=f"{caption} (from Google Drive)" if caption else "Imported from Google Drive",
                                    captured_at=datetime.utcnow(),
                                    status=PhotoStatus.APPROVED if auto_approve else PhotoStatus.PENDING,
                                    approved_by=user.id if auto_approve else None
                                )
                                db.add(photo)
                                photos_imported += 1

                            db.commit()

                        progress_bar.progress((i + 1) / num_photos)

                    st.success(f"✅ Successfully imported {photos_imported} photos for {len(selected_children)} child(ren)!")
                    st.balloons()

    st.divider()

    # Instructions for Google Drive setup
    with st.expander("ℹ️ How to Connect Google Drive"):
        st.markdown("""
        **Setup Instructions:**

        1. **Create a Shared Folder** in Google Drive
        2. **Upload Photos** to this folder
        3. **Get Shareable Link:**
           - Right-click folder → Share → Copy link
           - Set permissions to "Anyone with the link can view"
        4. **Paste Link Above** and import photos

        **Note:** In production, this uses Google Drive API for secure access.
        For demo purposes, we simulate the import process.
        """)

# ===== TAB 3: APPROVE PHOTOS =====
with tab3:
    st.subheader("✅ Approve Photos")

    with get_db() as db:
        pending_photos_db = db.query(Photo).filter(
            Photo.daycare_id == user.daycare_id,
            Photo.status == PhotoStatus.PENDING
        ).order_by(desc(Photo.uploaded_at)).all()
        # Extract photo data within session
        pending_photos = [{
            'id': p.id,
            'url': p.url,
            'caption': p.caption,
            'uploaded_at': p.uploaded_at
        } for p in pending_photos_db]

    if pending_photos:
        st.write(f"**{len(pending_photos)}** photos pending approval")

        # Display photos in grid
        cols = st.columns(3)
        for idx, photo in enumerate(pending_photos):
            with cols[idx % 3]:
                st.image(photo['url'], use_container_width=True)

                if photo['caption']:
                    st.caption(f"💬 {photo['caption']}")

                st.caption(f"📅 {photo['uploaded_at'].strftime('%b %d, %I:%M %p')}")

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Approve", key=f"approve_{photo['id']}", use_container_width=True):
                        with get_db() as db:
                            photo_to_update = db.query(Photo).filter(Photo.id == photo['id']).first()
                            photo_to_update.status = PhotoStatus.APPROVED
                            db.commit()
                        st.success("Approved!")
                        st.rerun()

                with col2:
                    if st.button("❌ Reject", key=f"reject_{photo['id']}", use_container_width=True):
                        with get_db() as db:
                            photo_to_delete = db.query(Photo).filter(Photo.id == photo['id']).first()
                            db.delete(photo_to_delete)
                            db.commit()
                        st.warning("Rejected!")
                        st.rerun()

                st.divider()
    else:
        st.info("✅ No photos pending approval!")

# ===== TAB 4: LOG ACTIVITY =====
with tab4:
    st.subheader("📝 Log Activity")

    # Get children
    with get_db() as db:
        children_db = db.query(Child).filter(Child.daycare_id == user.daycare_id).all()
        children = [{
            'id': c.id,
            'first_name': c.first_name,
            'last_name': c.last_name
        } for c in children_db]

    if not children:
        st.warning("No children found in your daycare.")
    else:
        with st.form("log_activity_form"):
            # Child selector (multi-select for group activities)
            child_names = {f"{child['first_name']} {child['last_name']}": child['id'] for child in children}
            selected_children = st.multiselect(
                "Select Children",
                options=list(child_names.keys())
            )

            # Activity type
            activity_type = st.selectbox(
                "Activity Type",
                options=["Meal", "Nap", "Play", "Learning", "Outdoor", "Art", "Diaper Change", "Other"]
            )

            # Time
            col1, col2 = st.columns(2)
            with col1:
                activity_date = st.date_input("Date", value=datetime.now())
            with col2:
                activity_time = st.time_input("Time", value=datetime.now().time())

            # Duration (for naps, meals, etc.)
            duration = st.number_input("Duration (minutes)", min_value=0, value=0)

            # Notes
            notes = st.text_area("Notes", placeholder="Additional details about this activity...")

            # Mood/Behavior
            mood = st.select_slider(
                "Child's Mood",
                options=["😢 Upset", "😐 Okay", "🙂 Good", "😊 Happy", "🤩 Excited"],
                value="🙂 Good"
            )

            submit = st.form_submit_button("💾 Save Activity", use_container_width=True)

            if submit:
                if not selected_children:
                    st.error("Please select at least one child")
                else:
                    # Combine date and time
                    activity_datetime = datetime.combine(activity_date, activity_time)

                    with get_db() as db:
                        for child_name in selected_children:
                            child_id = child_names[child_name]

                            activity = Activity(
                                id=str(uuid.uuid4()),
                                child_id=child_id,
                                daycare_id=user.daycare_id,
                                staff_id=user.id,
                                activity_type=activity_type.lower(),
                                activity_time=activity_datetime,
                                duration_minutes=duration if duration > 0 else None,
                                notes=notes,
                                mood=mood,
                                created_at=datetime.utcnow()
                            )
                            db.add(activity)
                        db.commit()

                    st.success(f"✅ Activity logged for {len(selected_children)} child(ren)!")

    st.divider()

    # Recent activities
    st.subheader("📋 Recent Activities (Today)")

    today = datetime.now().date()
    with get_db() as db:
        today_activities_db = db.query(Activity).filter(
            Activity.daycare_id == user.daycare_id,
            Activity.activity_time >= datetime.combine(today, datetime.min.time())
        ).order_by(desc(Activity.activity_time)).limit(20).all()
        # Extract activity data within session
        today_activities = [{
            'id': a.id,
            'child_id': a.child_id,
            'activity_type': a.activity_type,
            'activity_time': a.activity_time,
            'notes': a.notes,
            'mood': a.mood
        } for a in today_activities_db]

    if today_activities:
        for activity in today_activities:
            # Get child name from extracted data
            child = next((c for c in children if c['id'] == activity['child_id']), None)
            child_name = f"{child['first_name']} {child['last_name']}" if child else "Unknown"

            # Activity icon
            icons = {
                "meal": "🍽️",
                "nap": "😴",
                "play": "🎮",
                "learning": "📚",
                "outdoor": "🌳",
                "art": "🎨",
                "diaper change": "🧷",
                "other": "📝"
            }
            icon = icons.get(activity['activity_type'], "📝")

            with st.container():
                col1, col2, col3 = st.columns([2, 5, 2])
                with col1:
                    st.write(f"**{activity['activity_time'].strftime('%I:%M %p')}**")
                with col2:
                    st.write(f"{icon} **{activity['activity_type'].title()}** - {child_name}")
                    if activity['notes']:
                        st.caption(activity['notes'])
                with col3:
                    if activity['mood']:
                        st.write(activity['mood'])

                st.divider()
    else:
        st.info("No activities logged today yet.")

# ===== TAB 5: CHILDREN =====
with tab5:
    st.subheader("👶 Children in Daycare")

    with get_db() as db:
        children_db = db.query(Child).filter(Child.daycare_id == user.daycare_id).all()
        children = [{
            'id': c.id,
            'first_name': c.first_name,
            'last_name': c.last_name,
            'date_of_birth': c.date_of_birth,
            'allergies': c.allergies,
            'medical_notes': c.medical_notes,
            'parent_id': c.parent_id
        } for c in children_db]

    if children:
        st.write(f"**Total Children:** {len(children)}")

        # Search
        search = st.text_input("🔍 Search by name", "")

        # Filter children
        filtered_children = children
        if search:
            filtered_children = [
                c for c in children
                if search.lower() in f"{c['first_name']} {c['last_name']}".lower()
            ]

        # Display children
        for child in filtered_children:
            with st.expander(f"👶 {child['first_name']} {child['last_name']}"):
                col1, col2 = st.columns(2)

                with col1:
                    st.write(f"**Birthday:** {child['date_of_birth'].strftime('%B %d, %Y')}")

                    # Calculate age
                    today = datetime.now().date()
                    age_years = today.year - child['date_of_birth'].year
                    age_months = today.month - child['date_of_birth'].month
                    if age_months < 0:
                        age_years -= 1
                        age_months += 12

                    st.write(f"**Age:** {age_years} years, {age_months} months")

                    if child['allergies']:
                        st.warning(f"⚠️ **Allergies:** {child['allergies']}")

                    if child['medical_notes']:
                        st.info(f"🏥 **Medical Notes:** {child['medical_notes']}")

                with col2:
                    # Get parent info
                    if child['parent_id']:
                        with get_db() as db:
                            parent = db.query(User).filter(User.id == child['parent_id']).first()
                            if parent:
                                parent_data = {
                                    'first_name': parent.first_name,
                                    'last_name': parent.last_name,
                                    'email': parent.email,
                                    'phone': parent.phone
                                }
                            else:
                                parent_data = None

                        if parent_data:
                            st.write(f"**Parent:** {parent_data['first_name']} {parent_data['last_name']}")
                            st.write(f"**Email:** {parent_data['email']}")
                            if parent_data['phone']:
                                st.write(f"**Phone:** {parent_data['phone']}")

                    # Quick stats
                    week_ago = datetime.now() - timedelta(days=7)
                    with get_db() as db:
                        photo_count = db.query(Photo).filter(
                            Photo.child_id == child['id'],
                            Photo.uploaded_at >= week_ago
                        ).count()

                        activity_count = db.query(Activity).filter(
                            Activity.child_id == child['id'],
                            Activity.activity_time >= week_ago
                        ).count()

                    st.metric("Photos (7 days)", photo_count)
                    st.metric("Activities (7 days)", activity_count)
    else:
        st.info("No children in daycare yet.")

# ===== QUICK STATS =====
st.divider()
st.subheader("📊 Today's Statistics")

today = datetime.now().date()
with get_db() as db:
    # Photos uploaded today
    photos_today = db.query(Photo).filter(
        Photo.daycare_id == user.daycare_id,
        Photo.uploaded_at >= datetime.combine(today, datetime.min.time())
    ).count()

    # Activities logged today
    activities_today = db.query(Activity).filter(
        Photo.daycare_id == user.daycare_id,
        Activity.activity_time >= datetime.combine(today, datetime.min.time())
    ).count()

    # Pending photos
    pending_count = db.query(Photo).filter(
        Photo.daycare_id == user.daycare_id,
        Photo.status == PhotoStatus.PENDING
    ).count()

    # Get children count
    children_count = db.query(Child).filter(Child.daycare_id == user.daycare_id).count()

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("📸 Photos Today", photos_today)
with col2:
    st.metric("📝 Activities Today", activities_today)
with col3:
    st.metric("⏳ Pending Approval", pending_count)
with col4:
    st.metric("👶 Total Children", children_count)
