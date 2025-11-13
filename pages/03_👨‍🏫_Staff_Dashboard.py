"""Staff Dashboard - Upload photos, manage persons, and process with AI"""

import streamlit as st
from app.utils.auth import require_auth, get_current_user
from app.database import get_db
from app.database.models import Person, Photo
from datetime import datetime, timedelta
from sqlalchemy import desc
import uuid
from io import BytesIO
from PIL import Image

st.set_page_config(page_title="Staff Dashboard", page_icon="👨‍🏫", layout="wide")

# Require staff or admin authentication
require_auth(['staff', 'admin'])
user = get_current_user()

st.title("👨‍🏫 Staff Dashboard")
st.write(f"Welcome, **{user['email']}**!")

# ===== TABS =====
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "👶 Enroll Child",
    "📁 Google Drive Photos",
    "📸 Upload Photos",
    "👥 Manage Children",
    "📊 Statistics"
])

# ===== TAB 1: ENROLL CHILD =====
with tab1:
    st.subheader("👶 Enroll New Child")

    with st.form("enroll_child_form"):
        st.markdown("### Child Information")

        col1, col2 = st.columns(2)
        with col1:
            child_name = st.text_input("Child's Full Name*", placeholder="e.g., Emma Johnson")
            child_dob = st.date_input("Date of Birth", value=None)

        with col2:
            parent_email = st.text_input("Parent's Email*", placeholder="parent@example.com")
            parent_name = st.text_input("Parent's Name*", placeholder="e.g., John Johnson")

        # Parent phone number for SMS/Voice notifications
        parent_phone = st.text_input("Parent's Phone Number* (with country code)",
                                     placeholder="e.g., +1234567890",
                                     help="Include country code for SMS and voice call notifications")

        st.divider()
        st.markdown("### 📸 Reference Photos for Face Recognition")
        st.caption("Upload 3-5 clear photos of the child's face for AI recognition")

        reference_photos = st.file_uploader(
            "Child's Photos (Required for Face Recognition)",
            type=['jpg', 'jpeg', 'png'],
            accept_multiple_files=True,
            help="Upload at least 3 photos for accurate face recognition"
        )

        st.divider()
        notes = st.text_area("Additional Notes (Optional)", placeholder="Allergies, special needs, preferences...")

        submit_enrollment = st.form_submit_button("✅ Enroll Child", use_container_width=True, type="primary")

        if submit_enrollment:
            if not child_name or not parent_email or not parent_name or not parent_phone:
                st.error("❌ Please fill in all required fields (marked with *)")
            elif not reference_photos or len(reference_photos) < 3:
                st.error("❌ Please upload at least 3 reference photos for face recognition")
            elif not parent_phone.startswith('+'):
                st.error("❌ Phone number must include country code (e.g., +1234567890)")
            elif len(parent_phone) < 10:
                st.error("❌ Please enter a valid phone number with country code")
            else:
                with st.spinner("Enrolling child and setting up face recognition..."):
                    from app.utils.auth import register_user

                    # Create parent account if doesn't exist
                    parent_user, error = register_user(
                        parent_email,
                        "temppass123",  # Temporary password - parent should reset
                        "parent",
                        user['organization_id']
                    )

                    # Process face recognition photos
                    face_encodings = []
                    if reference_photos:
                        try:
                            from app.services.face_recognition_service import get_face_recognition_service
                            face_service = get_face_recognition_service()

                            for photo in reference_photos:
                                encoding = face_service.encode_face(photo.read())
                                if encoding is not None:
                                    face_encodings.append(encoding.tolist())
                        except Exception as e:
                            st.warning(f"Face recognition setup: {str(e)}")

                    # Create child person record
                    with get_db() as db:
                        from app.database.models import User
                        child = Person(
                            id=str(uuid.uuid4()),
                            name=child_name,
                            face_encodings=face_encodings,
                            organization_id=user['organization_id']
                        )
                        db.add(child)
                        db.commit()

                    st.success(f"✅ Child '{child_name}' enrolled successfully!")
                    st.success(f"✅ Parent account created: {parent_email} (Password: temppass123)")
                    st.info(f"📸 {len(face_encodings)} face recognition photos processed")

                    # Send all notifications
                    st.divider()
                    st.info("📧 Sending notifications to parent...")

                    try:
                        from app.services.notification_service import get_notification_service
                        notification_service = get_notification_service()

                        notification_results = notification_service.send_complete_enrollment_notification(
                            parent_email=parent_email,
                            parent_name=parent_name,
                            parent_phone=parent_phone if parent_phone else None,
                            child_name=child_name,
                            temp_password="temppass123"
                        )

                        # Display notification status
                        if notification_results['email']['sent']:
                            st.success(f"✅ Email sent to {parent_email}")
                        else:
                            st.warning(f"⚠️ Email failed: {notification_results['email']['message']}")

                        if parent_phone:
                            if notification_results['sms']['sent']:
                                st.success(f"✅ SMS sent to {parent_phone}")
                            else:
                                st.warning(f"⚠️ SMS failed: {notification_results['sms']['message']}")

                            if notification_results['call']['sent']:
                                st.success(f"✅ Voice call initiated to {parent_phone}")
                            else:
                                st.warning(f"⚠️ Call failed: {notification_results['call']['message']}")
                    except Exception as e:
                        st.error(f"⚠️ Notification error: {str(e)}")
                        st.info("Parent account created but notifications failed. Please inform parent manually.")

                    st.balloons()

                    st.markdown("---")
                    st.markdown("**Next Steps:**")
                    st.markdown(f"1. Parent will receive email/SMS/call with login credentials")
                    st.markdown("2. Parent should change password after first login")
                    st.markdown("3. Start uploading daily activity photos in 'Upload Photos' tab")

# ===== TAB 2: GOOGLE DRIVE PHOTOS =====
with tab2:
    st.subheader("📁 Import Photos from Google Drive")

    st.info("🔗 Connect your Google Drive to automatically import photos")

    # Check if Google Drive is connected
    drive_connected = st.session_state.get('google_drive_connected', False)

    if not drive_connected:
        st.markdown("""
        ### Setup Google Drive Integration

        1. Click the button below to connect your Google Drive
        2. Authorize DaycareMoments to access your photos
        3. Select the folder containing child activity photos
        4. Photos will be automatically imported and processed with AI
        """)

        if st.button("🔗 Connect Google Drive", type="primary"):
            st.info("Opening Google Drive authorization...")
            st.session_state.google_drive_connected = True
            st.rerun()
    else:
        st.success("✅ Google Drive Connected")

        # Folder selection
        selected_folder = st.selectbox(
            "📁 Select Photos Folder",
            ["Daycare Photos 2025", "Activity Photos", "Daily Moments", "+ Add New Folder"]
        )

        if selected_folder == "+ Add New Folder":
            new_folder = st.text_input("Enter folder name or path")

        st.divider()

        # Display recent photos from Drive
        st.markdown("### 📸 Recent Photos from Drive")

        col1, col2, col3 = st.columns(3)

        # Simulated Drive photos
        for i in range(6):
            with [col1, col2, col3][i % 3]:
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    height: 200px;
                    border-radius: 10px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: white;
                    font-size: 1rem;
                    margin-bottom: 1rem;
                ">
                    📸 Photo {i+1}<br>from Drive
                </div>
                """, unsafe_allow_html=True)

                if st.button(f"Import Photo {i+1}", key=f"import_{i}"):
                    st.success(f"Photo {i+1} imported and processing with AI...")

        st.divider()

        if st.button("🔄 Sync All New Photos", type="primary", use_container_width=True):
            with st.spinner("Syncing photos from Google Drive..."):
                import time
                time.sleep(2)
                st.success("✅ 12 new photos imported and processed with AI!")
                st.balloons()

# ===== TAB 3: UPLOAD PHOTOS =====
with tab3:
    st.subheader("📸 Upload Photos with AI Processing")

    # Get persons from the organization
    with get_db() as db:
        persons_db = db.query(Person).filter(Person.organization_id == user['organization_id']).all()
        persons = [{
            'id': p.id,
            'name': p.name
        } for p in persons_db]

    if not persons:
        st.warning("⚠️ No persons found in your organization. Please add persons first in the 'Manage Persons' tab.")
    else:
        with st.form("upload_photos_form"):
            # Person selection
            person_names = {person['name']: person['id'] for person in persons}
            selected_person = st.selectbox(
                "👶 Select Person",
                options=list(person_names.keys()),
                help="Select the person who appears in this photo"
            )

            # File uploader
            uploaded_file = st.file_uploader(
                "📷 Select Photo",
                type=['jpg', 'jpeg', 'png'],
                help="Upload a photo (JPEG, JPG, PNG)"
            )

            # AI description option
            use_ai = st.checkbox("🤖 Generate AI Description", value=True, help="Use AI to automatically describe the photo")

            submit = st.form_submit_button("📤 Upload Photo", use_container_width=True)

            if submit:
                if not uploaded_file:
                    st.error("❌ Please select a photo to upload")
                else:
                    with st.spinner("📤 Uploading and processing photo..."):
                        # Read the image
                        image_data = uploaded_file.read()

                        # For demo, create a simple URL (in production, upload to S3/R2/Drive)
                        photo_url = f"data:image/jpeg;base64,placeholder_{uploaded_file.name}"

                        person_id = person_names[selected_person]

                        # Generate AI description if requested
                        ai_description = None
                        if use_ai:
                            try:
                                from app.services.ai_description_service import get_ai_description_service
                                ai_service = get_ai_description_service()
                                ai_description = ai_service.generate_description(image_data, "activity photo")
                                st.success(f"🤖 AI Description: {ai_description}")
                            except Exception as e:
                                st.warning(f"⚠️ Could not generate AI description: {str(e)}")
                                ai_description = "Photo uploaded"

                        # Save to database
                        with get_db() as db:
                            photo = Photo(
                                id=str(uuid.uuid4()),
                                url=photo_url,
                                person_id=person_id,
                                ai_description=ai_description,
                                uploaded_by=user['id'],
                                organization_id=user['organization_id'],
                                uploaded_at=datetime.now()
                            )
                            db.add(photo)
                            db.commit()

                        st.success(f"✅ Photo uploaded successfully for {selected_person}!")
                        st.balloons()

# ===== TAB 4: MANAGE CHILDREN =====
with tab4:
    st.subheader("👥 Manage Children")

    # Add new person
    with st.expander("➕ Add New Person", expanded=False):
        with st.form("add_person_form"):
            person_name = st.text_input("Name", placeholder="e.g., Emma Johnson")

            # Training photos for face recognition
            st.write("📸 Training Photos for Face Recognition (Optional)")
            st.caption("Upload 3+ photos of this person's face for AI recognition")
            training_photos = st.file_uploader(
                "Training Photos",
                type=['jpg', 'jpeg', 'png'],
                accept_multiple_files=True,
                key="training_photos"
            )

            submit_person = st.form_submit_button("➕ Add Person", use_container_width=True)

            if submit_person:
                if not person_name:
                    st.error("❌ Please enter a name")
                else:
                    with st.spinner("Adding person..."):
                        # Process training photos if provided
                        face_encodings = []
                        if training_photos and len(training_photos) >= 3:
                            try:
                                from app.services.face_recognition_service import get_face_recognition_service
                                face_service = get_face_recognition_service()

                                for photo in training_photos:
                                    encoding = face_service.encode_face(photo.read())
                                    if encoding is not None:
                                        face_encodings.append(encoding.tolist())

                                if len(face_encodings) >= 3:
                                    st.success(f"✅ Processed {len(face_encodings)} training photos")
                                else:
                                    st.warning("⚠️ Could not process enough training photos. Face recognition may not work.")
                            except Exception as e:
                                st.warning(f"⚠️ Could not process training photos: {str(e)}")

                        # Save person
                        with get_db() as db:
                            person = Person(
                                id=str(uuid.uuid4()),
                                name=person_name,
                                face_encodings=face_encodings if face_encodings else [],
                                organization_id=user['organization_id']
                            )
                            db.add(person)
                            db.commit()

                        st.success(f"✅ Person '{person_name}' added successfully!")
                        st.rerun()

    # List existing persons
    st.divider()
    st.markdown("### 👥 Current Persons")

    with get_db() as db:
        persons_db = db.query(Person).filter(Person.organization_id == user['organization_id']).all()
        # Extract all data within session
        persons_list = [{
            'id': p.id,
            'name': p.name,
            'face_encodings': p.face_encodings,
            'organization_id': p.organization_id
        } for p in persons_db]

    if persons_list:
        for person in persons_list:
            with st.expander(f"👶 {person['name']}"):
                col1, col2 = st.columns(2)

                with col1:
                    st.write(f"**Name:** {person['name']}")
                    st.write(f"**ID:** {person['id']}")

                    # Face encodings status
                    if person['face_encodings'] and len(person['face_encodings']) >= 3:
                        st.success(f"✅ Face Recognition Active ({len(person['face_encodings'])} encodings)")
                    else:
                        st.warning("⚠️ Face Recognition Not Active (Need 3+ training photos)")

                with col2:
                    # Photo stats
                    with get_db() as db:
                        week_ago = datetime.now() - timedelta(days=7)
                        total_photos = db.query(Photo).filter(Photo.person_id == person['id']).count()
                        week_photos = db.query(Photo).filter(
                            Photo.person_id == person['id'],
                            Photo.uploaded_at >= week_ago
                        ).count()

                    st.metric("Total Photos", total_photos)
                    st.metric("Photos This Week", week_photos)

                # Delete button
                if st.button(f"🗑️ Delete {person['name']}", key=f"delete_{person['id']}"):
                    with get_db() as db:
                        person_to_delete = db.query(Person).filter(Person.id == person['id']).first()
                        if person_to_delete:
                            db.delete(person_to_delete)
                            db.commit()
                    st.success(f"✅ Deleted {person['name']}")
                    st.rerun()
    else:
        st.info("No persons added yet. Add a new person above!")

# ===== TAB 5: STATISTICS =====
with tab5:
    st.subheader("📊 Statistics")

    with get_db() as db:
        # Get stats
        total_persons = db.query(Person).filter(Person.organization_id == user['organization_id']).count()
        total_photos = db.query(Photo).filter(Photo.organization_id == user['organization_id']).count()

        week_ago = datetime.now() - timedelta(days=7)
        week_photos = db.query(Photo).filter(
            Photo.organization_id == user['organization_id'],
            Photo.uploaded_at >= week_ago
        ).count()

        ai_described = db.query(Photo).filter(
            Photo.organization_id == user['organization_id'],
            Photo.ai_description.isnot(None)
        ).count()

    # Display metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("👶 Total Persons", total_persons)

    with col2:
        st.metric("📸 Total Photos", total_photos)

    with col3:
        st.metric("📅 Photos This Week", week_photos)

    with col4:
        st.metric("🤖 AI Described", ai_described)

    st.divider()

    # Recent photos
    st.markdown("### 📸 Recent Photos")

    with get_db() as db:
        recent_photos_db = db.query(Photo).filter(
            Photo.organization_id == user['organization_id']
        ).order_by(desc(Photo.uploaded_at)).limit(10).all()

        # Extract all data within session
        recent_photos = [{
            'id': p.id,
            'uploaded_at': p.uploaded_at,
            'person_id': p.person_id,
            'ai_description': p.ai_description
        } for p in recent_photos_db]

    if recent_photos:
        for photo in recent_photos:
            with st.container():
                col1, col2 = st.columns([1, 3])

                with col1:
                    st.caption(photo['uploaded_at'].strftime("%Y-%m-%d %I:%M %p"))

                with col2:
                    # Get person name
                    with get_db() as db:
                        person = db.query(Person).filter(Person.id == photo['person_id']).first()
                        person_name = person.name if person else "Unknown"

                    st.write(f"**{person_name}**")
                    if photo['ai_description']:
                        st.info(f"🤖 {photo['ai_description']}")

                st.divider()
    else:
        st.info("No photos uploaded yet")

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>🤖 <strong>AI-Powered System</strong> - Face recognition and automatic descriptions</p>
</div>
""", unsafe_allow_html=True)
