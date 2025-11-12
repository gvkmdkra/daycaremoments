"""
Child Enrollment Page - Add children with face recognition training
Staff can enroll new children and upload 3-5 training photos for face recognition
"""

import streamlit as st
from datetime import datetime, date
from app.utils.auth import require_auth, get_current_user
from app.database import get_db
from app.database.models import Child, User, UserRole
from app.services.face_recognition_service import get_face_recognition_service
from app.utils.ui_theme import apply_professional_theme
import io

st.set_page_config(page_title="Enroll Child", page_icon="👶", layout="wide")

# Apply professional theme
apply_professional_theme()

# Require staff authentication
require_auth(['staff', 'admin'])
user = get_current_user()

st.title("👶 Enroll New Child")
st.write("Add a new child to the daycare with face recognition training")

# Initialize face recognition service
face_service = get_face_recognition_service()

# ===== CHILD INFORMATION FORM =====
st.subheader("📋 Child Information")

with st.form("child_enrollment_form", clear_on_submit=True):
    col1, col2 = st.columns(2)

    with col1:
        first_name = st.text_input("First Name *", placeholder="Emma")
        last_name = st.text_input("Last Name *", placeholder="Johnson")
        date_of_birth = st.date_input(
            "Date of Birth *",
            min_value=date(2015, 1, 1),
            max_value=date.today(),
            value=None
        )
        gender = st.selectbox("Gender", options=["", "Female", "Male", "Other"])

    with col2:
        # Get parents for selection
        with get_db() as db:
            parents = db.query(User).filter(
                User.daycare_id == user.daycare_id,
                User.role == UserRole.PARENT,
                User.is_active == True
            ).all()

            parent_options = {
                f"{p.first_name} {p.last_name} ({p.email})": p.id
                for p in parents
            }

        selected_parent = st.selectbox(
            "Primary Parent",
            options=[""] + list(parent_options.keys()),
            help="Link child to a parent account"
        )

        allergies = st.text_area("Allergies", placeholder="Peanuts, dairy, etc.")
        medical_notes = st.text_area("Medical Notes", placeholder="Any medical conditions or special needs")

    st.divider()

    # ===== FACE RECOGNITION TRAINING =====
    st.subheader("📸 Face Recognition Training")
    st.info("""
    **Upload 3-5 clear photos of the child's face for face recognition training:**
    - Photos should show the child's face clearly
    - Include different angles and expressions
    - Good lighting is important
    - Multiple photos improve recognition accuracy
    """)

    training_photos = st.file_uploader(
        "Upload Training Photos (3-5 recommended)",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True,
        help="Upload 3-5 clear photos of the child's face"
    )

    # Show preview of uploaded photos
    if training_photos:
        st.write(f"**{len(training_photos)} photo(s) uploaded**")
        cols = st.columns(min(len(training_photos), 5))
        for idx, photo in enumerate(training_photos[:5]):
            with cols[idx]:
                st.image(photo, use_container_width=True)

    st.divider()

    # Form submission
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.caption("* Required fields")
    with col3:
        submitted = st.form_submit_button("✅ Enroll Child", use_container_width=True, type="primary")

# ===== PROCESS ENROLLMENT =====
if submitted:
    # Validation
    errors = []

    if not first_name or not first_name.strip():
        errors.append("First name is required")
    if not last_name or not last_name.strip():
        errors.append("Last name is required")
    if not date_of_birth:
        errors.append("Date of birth is required")
    if not training_photos or len(training_photos) < 3:
        errors.append("Please upload at least 3 training photos for face recognition")
    if len(training_photos) > 10:
        errors.append("Maximum 10 training photos allowed")

    if errors:
        st.error("**Enrollment Errors:**")
        for error in errors:
            st.error(f"• {error}")
    else:
        # Process enrollment
        with st.spinner("Enrolling child and training face recognition..."):
            try:
                with get_db() as db:
                    # Create child record
                    new_child = Child(
                        first_name=first_name.strip(),
                        last_name=last_name.strip(),
                        date_of_birth=date_of_birth,
                        gender=gender if gender else None,
                        allergies=allergies.strip() if allergies else None,
                        medical_notes=medical_notes.strip() if medical_notes else None,
                        daycare_id=user.daycare_id,
                        parent_id=parent_options.get(selected_parent) if selected_parent else None,
                        is_active=True,
                        face_encodings=[],  # Will be populated during training
                        training_photo_count=0
                    )

                    db.add(new_child)
                    db.flush()  # Get the child ID

                    child_id = new_child.id

                    # Add parent relationship (many-to-many)
                    if selected_parent:
                        parent = db.query(User).filter(
                            User.id == parent_options[selected_parent]
                        ).first()
                        if parent:
                            new_child.parents.append(parent)

                    db.commit()

                # Process training photos
                st.info("📸 Processing training photos for face recognition...")

                training_images = []
                for photo in training_photos:
                    photo_bytes = photo.read()
                    training_images.append(photo_bytes)

                # Train face recognition
                training_result = face_service.train_child(child_id, training_images)

                if training_result["success"]:
                    st.success(f"""
                    ✅ **Child Enrolled Successfully!**

                    **{first_name} {last_name}** has been added to the daycare.

                    **Face Recognition Training:**
                    - ✅ {training_result['encodings_added']} face encodings extracted
                    - ✅ Total encodings: {training_result['total_encodings']}
                    - ⚠️ {training_result['failed_images']} photos failed (no face detected)

                    The system will now automatically recognize {first_name} in uploaded photos!
                    """)

                    # Show next steps
                    st.info("""
                    **Next Steps:**
                    1. Go to "Upload Photos" to start adding daily photos
                    2. The system will automatically detect and tag {first_name}
                    3. Parents can view their child's photos in the Parent Portal
                    """.replace("{first_name}", first_name))

                else:
                    st.error(f"""
                    ⚠️ **Child enrolled but face training failed:**

                    {training_result.get('error', 'Unknown error')}

                    You can add more training photos later to enable face recognition.
                    """)

            except Exception as e:
                st.error(f"❌ **Enrollment failed:** {str(e)}")
                import traceback
                st.error(traceback.format_exc())

# ===== ENROLLED CHILDREN LIST =====
st.divider()
st.subheader("📋 Recently Enrolled Children")

with get_db() as db:
    recent_children = db.query(Child).filter(
        Child.daycare_id == user.daycare_id,
        Child.is_active == True
    ).order_by(Child.created_at.desc()).limit(10).all()

    if recent_children:
        # Create data for display
        children_data = []
        for child in recent_children:
            parent_names = ", ".join([
                f"{p.first_name} {p.last_name}"
                for p in child.parents
            ]) if child.parents else "No parent linked"

            children_data.append({
                "Name": f"{child.first_name} {child.last_name}",
                "Age": f"{(date.today() - child.date_of_birth).days // 365} years",
                "Parent(s)": parent_names,
                "Training Photos": child.training_photo_count,
                "Face Recognition": "✅ Trained" if child.training_photo_count >= 3 else "⚠️ Needs Training",
                "Enrolled": child.created_at.strftime("%b %d, %Y")
            })

        import pandas as pd
        df = pd.DataFrame(children_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No children enrolled yet. Start by enrolling your first child above!")

# ===== STATISTICS =====
with st.sidebar:
    st.header("📊 Enrollment Statistics")

    with get_db() as db:
        total_children = db.query(Child).filter(
            Child.daycare_id == user.daycare_id,
            Child.is_active == True
        ).count()

        trained_children = db.query(Child).filter(
            Child.daycare_id == user.daycare_id,
            Child.is_active == True,
            Child.training_photo_count >= 3
        ).count()

        total_parents = db.query(User).filter(
            User.daycare_id == user.daycare_id,
            User.role == UserRole.PARENT,
            User.is_active == True
        ).count()

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Children", total_children)
    with col2:
        st.metric("Face Trained", trained_children)

    st.metric("Total Parents", total_parents)

    if total_children > 0:
        training_rate = round(trained_children / total_children * 100)
        st.progress(training_rate / 100)
        st.caption(f"{training_rate}% of children have face recognition trained")

    st.divider()

    st.subheader("💡 Tips")
    st.info("""
    **Best practices for training photos:**
    - Use high-quality, well-lit photos
    - Include different angles
    - Capture various expressions
    - Avoid sunglasses or face coverings
    - One face per training photo
    """)
