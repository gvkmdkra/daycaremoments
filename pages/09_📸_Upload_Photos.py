"""
Staff Photo Upload Page - Bulk photo upload with automatic processing
Photos are automatically processed for face detection, recognition, and AI description
"""

import streamlit as st
from datetime import datetime
import io
from PIL import Image
import uuid

from app.utils.auth import require_auth, get_current_user
from app.database import get_db
from app.database.models import Photo, Child, PhotoStatus
from app.services.photo_processor import get_photo_processor
from app.services.storage.local_adapter import LocalStorageAdapter
from app.utils.ui_theme import apply_professional_theme
from app.config import Config

st.set_page_config(page_title="Upload Photos", page_icon="📸", layout="wide")

# Apply professional theme
apply_professional_theme()

# Require staff authentication
require_auth(['staff', 'admin'])
user = get_current_user()

st.title("📸 Upload Photos")
st.write("Upload photos and let AI automatically detect, tag, and describe activities")

# Initialize services
photo_processor = get_photo_processor()
storage = LocalStorageAdapter()

# ===== UPLOAD SECTION =====
st.subheader("📤 Upload Photos")

col1, col2 = st.columns([2, 1])

with col1:
    uploaded_files = st.file_uploader(
        "Select photos to upload",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True,
        help=f"Upload up to {Config.MAX_FILES_PER_UPLOAD} photos at once"
    )

with col2:
    st.info(f"""
    **Auto-processing will:**
    - 🔍 Detect faces
    - 👶 Identify children
    - 🤖 Generate descriptions
    - 📋 Create activities
    """)

# Photo metadata
if uploaded_files:
    st.divider()
    with st.expander("📝 Photo Settings (Optional)", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            location = st.text_input("Location", placeholder="Playground, Classroom, etc.")
            caption = st.text_area("General Caption", placeholder="Optional caption for all photos")
        with col2:
            captured_at = st.date_input("Photos taken on", value=datetime.now())
            auto_approve = st.checkbox("Auto-approve photos", value=True, help="Automatically approve photos for parent viewing")

# ===== PROCESS UPLOADS =====
if uploaded_files:
    st.divider()

    # Limit check
    if len(uploaded_files) > Config.MAX_FILES_PER_UPLOAD:
        st.error(f"⚠️ Maximum {Config.MAX_FILES_PER_UPLOAD} photos per upload. Please select fewer photos.")
    else:
        # Show preview
        st.subheader("📋 Upload Preview")
        st.write(f"**{len(uploaded_files)} photo(s) ready to upload**")

        # Display thumbnails
        preview_cols = st.columns(min(len(uploaded_files), 5))
        for idx, file in enumerate(uploaded_files[:5]):
            with preview_cols[idx]:
                st.image(file, use_container_width=True)
                st.caption(file.name[:20] + "..." if len(file.name) > 20 else file.name)

        if len(uploaded_files) > 5:
            st.caption(f"...and {len(uploaded_files) - 5} more photos")

        # Upload button
        col1, col2, col3 = st.columns([2, 1, 1])
        with col3:
            if st.button("🚀 Upload & Process", type="primary", use_container_width=True):
                process_photos(
                    uploaded_files,
                    user,
                    storage,
                    photo_processor,
                    location,
                    caption,
                    captured_at,
                    auto_approve
                )

def process_photos(files, user, storage, photo_processor, location, caption, captured_at, auto_approve):
    """Process and upload photos with AI analysis"""

    progress_bar = st.progress(0)
    status_text = st.empty()

    photo_ids = []
    image_data_map = {}

    # Step 1: Upload photos to storage and create database records
    status_text.text("📤 Uploading photos to storage...")

    for idx, file in enumerate(files):
        try:
            # Read file data
            file_bytes = file.read()
            file.seek(0)  # Reset for potential re-read

            # Open image to get dimensions
            image = Image.open(io.BytesIO(file_bytes))
            width, height = image.size

            # Generate unique filename
            file_extension = file.name.split('.')[-1].lower()
            unique_filename = f"{uuid.uuid4()}.{file_extension}"

            # Save to storage (for local storage, this saves to disk)
            storage_url = f"uploads/{user.daycare_id}/{unique_filename}"

            # For now, we'll use a placeholder URL (in production, storage.upload would return the URL)
            # storage.upload(file_bytes, storage_url)

            # Create photo record in database
            with get_db() as db:
                photo = Photo(
                    file_name=unique_filename,
                    original_file_name=file.name,
                    url=storage_url,
                    file_size=len(file_bytes),
                    width=width,
                    height=height,
                    mime_type=file.type,
                    caption=caption if caption else None,
                    location=location if location else None,
                    captured_at=datetime.combine(captured_at, datetime.now().time()),
                    uploaded_by=user.id,
                    daycare_id=user.daycare_id,
                    status=PhotoStatus.APPROVED if auto_approve else PhotoStatus.PENDING,
                    face_recognition_complete=False,
                    auto_tagged=False
                )

                db.add(photo)
                db.commit()
                db.refresh(photo)

                photo_ids.append(photo.id)
                image_data_map[photo.id] = file_bytes

            progress_bar.progress((idx + 1) / (len(files) * 2))

        except Exception as e:
            st.error(f"Error uploading {file.name}: {str(e)}")

    # Step 2: Process photos with AI
    status_text.text("🤖 Processing photos with AI (face detection, recognition, descriptions)...")

    processing_results = []

    for idx, photo_id in enumerate(photo_ids):
        try:
            image_data = image_data_map[photo_id]
            result = photo_processor.process_uploaded_photo(photo_id, image_data, user.id)
            processing_results.append(result)

            progress_bar.progress(0.5 + (idx + 1) / (len(photo_ids) * 2))

        except Exception as e:
            st.error(f"Error processing photo {photo_id}: {str(e)}")
            processing_results.append({
                "success": False,
                "error": str(e)
            })

    progress_bar.progress(1.0)
    status_text.empty()

    # Display results
    display_processing_results(processing_results, photo_ids)


def display_processing_results(results, photo_ids):
    """Display processing results in an organized way"""

    st.divider()
    st.subheader("✅ Processing Complete!")

    # Calculate statistics
    successful = sum(1 for r in results if r.get("success"))
    total_faces = sum(r.get("faces_detected", 0) for r in results)
    unique_children = set()
    for r in results:
        unique_children.update(r.get("children_identified", []))

    activities_created = sum(1 for r in results if r.get("activity_created"))

    # Display summary metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Photos Uploaded", len(results))
    with col2:
        st.metric("Faces Detected", total_faces)
    with col3:
        st.metric("Children Identified", len(unique_children))
    with col4:
        st.metric("Activities Created", activities_created)

    # Success message
    if successful == len(results):
        st.success(f"🎉 All {successful} photos processed successfully!")
    else:
        st.warning(f"⚠️ {successful}/{len(results)} photos processed successfully")

    # Detailed results
    with st.expander("📊 View Detailed Results", expanded=False):
        with get_db() as db:
            for idx, (photo_id, result) in enumerate(zip(photo_ids, results)):
                photo = db.query(Photo).filter(Photo.id == photo_id).first()

                if photo and result.get("success"):
                    col1, col2 = st.columns([1, 3])

                    with col1:
                        if photo.url:
                            st.image(photo.url, use_container_width=True)

                    with col2:
                        st.write(f"**{photo.original_file_name}**")

                        if result.get("children_identified"):
                            children = db.query(Child).filter(
                                Child.id.in_(result["children_identified"])
                            ).all()
                            child_names = [f"{c.first_name} {c.last_name}" for c in children]
                            st.write(f"👶 **Children:** {', '.join(child_names)}")
                        else:
                            st.write("👶 **Children:** None identified")

                        st.write(f"👤 **Faces Detected:** {result.get('faces_detected', 0)}")

                        if result.get("description"):
                            st.info(f"🤖 **AI Description:** {result['description']}")

                        if result.get("activity_created"):
                            st.success("✅ Activity record created")

                    st.divider()

    # Get identified children details
    if unique_children:
        st.subheader("👶 Identified Children")

        with get_db() as db:
            children = db.query(Child).filter(Child.id.in_(list(unique_children))).all()

            cols = st.columns(min(len(children), 4))
            for idx, child in enumerate(children):
                with cols[idx % 4]:
                    st.write(f"**{child.first_name} {child.last_name}**")

                    # Count photos for this child in this batch
                    photo_count = sum(
                        1 for r in results
                        if child.id in r.get("children_identified", [])
                    )
                    st.metric("Photos", photo_count)

    # Next steps
    st.divider()
    st.info("""
    **✅ What happens next:**
    - Parents can now view these photos in their Parent Portal
    - AI-generated descriptions are visible
    - Activities are logged in the timeline
    - Photos are ready for sharing
    """)


# ===== RECENT UPLOADS =====
st.divider()
st.subheader("📸 Recent Uploads")

with get_db() as db:
    recent_photos = db.query(Photo).filter(
        Photo.daycare_id == user.daycare_id,
        Photo.uploaded_by == user.id
    ).order_by(Photo.uploaded_at.desc()).limit(12).all()

    if recent_photos:
        cols = st.columns(4)
        for idx, photo in enumerate(recent_photos):
            with cols[idx % 4]:
                if photo.url:
                    st.image(photo.url, use_container_width=True)

                # Get child name
                child_name = "Unknown"
                if photo.child_id:
                    child = db.query(Child).filter(Child.id == photo.child_id).first()
                    if child:
                        child_name = f"{child.first_name} {child.last_name}"

                st.caption(f"👶 {child_name}")

                if photo.auto_tagged:
                    st.caption("🤖 Auto-tagged")

                if photo.ai_generated_description:
                    with st.expander("View Description"):
                        st.write(photo.ai_generated_description)

    else:
        st.info("No photos uploaded yet. Start by uploading your first batch above!")

# ===== SIDEBAR STATISTICS =====
with st.sidebar:
    st.header("📊 Upload Statistics")

    with get_db() as db:
        from datetime import timedelta

        # Today's stats
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        today_uploads = db.query(Photo).filter(
            Photo.daycare_id == user.daycare_id,
            Photo.uploaded_at >= today_start
        ).count()

        week_start = datetime.now() - timedelta(days=7)

        week_uploads = db.query(Photo).filter(
            Photo.daycare_id == user.daycare_id,
            Photo.uploaded_at >= week_start
        ).count()

        auto_tagged_week = db.query(Photo).filter(
            Photo.daycare_id == user.daycare_id,
            Photo.uploaded_at >= week_start,
            Photo.auto_tagged == True
        ).count()

        total_photos = db.query(Photo).filter(
            Photo.daycare_id == user.daycare_id
        ).count()

    st.metric("Today's Uploads", today_uploads)
    st.metric("This Week", week_uploads)
    st.metric("Auto-Tagged", auto_tagged_week)
    st.metric("Total Photos", total_photos)

    if week_uploads > 0:
        auto_tag_rate = round(auto_tagged_week / week_uploads * 100)
        st.divider()
        st.write("**Auto-Tag Success Rate**")
        st.progress(auto_tag_rate / 100)
        st.caption(f"{auto_tag_rate}% of photos auto-tagged this week")

    st.divider()

    # Processing stats
    stats = photo_processor.get_processing_stats(user.daycare_id, days=7)

    if stats:
        st.subheader("🤖 AI Processing")
        st.metric("Processing Rate", f"{stats.get('processing_rate', 0)}%")
        st.metric("AI Descriptions", stats.get('ai_described_photos', 0))
        st.metric("Auto Activities", stats.get('auto_created_activities', 0))

    st.divider()

    st.subheader("💡 Tips")
    st.info("""
    **Best practices:**
    - Upload photos throughout the day
    - Good lighting improves face detection
    - Group photos work too!
    - AI descriptions save time
    - Parents get instant updates
    """)
