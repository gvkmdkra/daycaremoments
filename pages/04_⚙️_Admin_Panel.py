"""Admin Panel - Manage users and organization settings"""

import streamlit as st
from app.utils.auth import require_auth, get_current_user, register_user
from app.database import get_db
from app.database.models import User, Person, Photo, Organization
from datetime import datetime, timedelta
from sqlalchemy import desc, func
import uuid

st.set_page_config(page_title="Admin Panel", page_icon="⚙️", layout="wide")

# Require admin authentication
require_auth(['admin'])
user = get_current_user()

st.title("⚙️ Admin Panel")
st.write(f"Welcome, **{user['email']}**!")

# Get organization info
with get_db() as db:
    org_db = db.query(Organization).filter(Organization.id == user['organization_id']).first()
    if not org_db:
        st.error("Organization not found!")
        st.stop()
    # Extract data while in session
    org_data = {
        'id': org_db.id,
        'name': org_db.name,
        'email': org_db.email
    }

st.info(f"Managing: **{org_data['name']}**")

# ===== TABS =====
tab1, tab2, tab3 = st.tabs(["👥 Users", "📊 Analytics", "⚙️ Settings"])

# ===== TAB 1: USERS =====
with tab1:
    st.subheader("👥 User Management")

    # Add new user section
    with st.expander("➕ Add New User", expanded=False):
        with st.form("add_user_form"):
            new_email = st.text_input("Email", placeholder="user@example.com")
            new_password = st.text_input("Password", type="password", placeholder="Minimum 6 characters")
            new_role = st.selectbox("Role", options=["parent", "staff", "admin"])

            submit_user = st.form_submit_button("➕ Add User", use_container_width=True)

            if submit_user:
                if not new_email or not new_password:
                    st.error("❌ Please enter both email and password")
                elif len(new_password) < 6:
                    st.error("❌ Password must be at least 6 characters")
                else:
                    new_user, error = register_user(new_email, new_password, new_role, user['organization_id'])
                    if new_user:
                        st.success(f"✅ User {new_email} added successfully with role: {new_role}")
                        st.rerun()
                    else:
                        st.error(f"❌ Failed to add user: {error}")

    # List existing users
    st.divider()
    st.markdown("### 👥 Current Users")

    with get_db() as db:
        users_db = db.query(User).filter(User.organization_id == user['organization_id']).all()
        users = [{
            'id': u.id,
            'email': u.email,
            'role': u.role,
            'organization_id': u.organization_id
        } for u in users_db]

    if users:
        for usr in users:
            with st.expander(f"👤 {usr['email']} ({usr['role']})"):
                col1, col2 = st.columns(2)

                with col1:
                    st.write(f"**Email:** {usr['email']}")
                    st.write(f"**Role:** {usr['role']}")
                    st.write(f"**ID:** {usr['id']}")

                with col2:
                    # Get photo stats for this user if they're staff
                    if usr['role'] == 'staff':
                        with get_db() as db:
                            photos_uploaded = db.query(Photo).filter(Photo.uploaded_by == usr['id']).count()
                        st.metric("Photos Uploaded", photos_uploaded)

                # Delete button (can't delete self)
                if usr['id'] != user['id']:
                    if st.button(f"🗑️ Delete {usr['email']}", key=f"delete_user_{usr['id']}"):
                        with get_db() as db:
                            user_to_delete = db.query(User).filter(User.id == usr['id']).first()
                            if user_to_delete:
                                db.delete(user_to_delete)
                                db.commit()
                        st.success(f"✅ Deleted {usr['email']}")
                        st.rerun()
                else:
                    st.caption("🔒 You cannot delete your own account")
    else:
        st.info("No users found")

# ===== TAB 2: ANALYTICS =====
with tab2:
    st.subheader("📊 System Analytics")

    with get_db() as db:
        # Get stats
        total_users = db.query(User).filter(User.organization_id == user['organization_id']).count()
        total_persons = db.query(Person).filter(Person.organization_id == user['organization_id']).count()
        total_photos = db.query(Photo).filter(Photo.organization_id == user['organization_id']).count()

        # Role breakdown
        staff_count = db.query(User).filter(
            User.organization_id == user['organization_id'],
            User.role == 'staff'
        ).count()

        parent_count = db.query(User).filter(
            User.organization_id == user['organization_id'],
            User.role == 'parent'
        ).count()

        admin_count = db.query(User).filter(
            User.organization_id == user['organization_id'],
            User.role == 'admin'
        ).count()

        # Recent activity
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
        st.metric("👥 Total Users", total_users)
        st.caption(f"Staff: {staff_count} | Parents: {parent_count} | Admins: {admin_count}")

    with col2:
        st.metric("👶 Total Persons", total_persons)

    with col3:
        st.metric("📸 Total Photos", total_photos)

    with col4:
        st.metric("📅 Photos This Week", week_photos)

    st.divider()

    # More detailed stats
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🤖 AI Usage")
        st.metric("AI Descriptions Generated", ai_described)
        if total_photos > 0:
            ai_percentage = (ai_described / total_photos) * 100
            st.progress(ai_percentage / 100)
            st.caption(f"{ai_percentage:.1f}% of photos have AI descriptions")

    with col2:
        st.markdown("### 📈 Growth")
        # Photos per day average
        if total_photos > 0:
            with get_db() as db:
                oldest_photo = db.query(Photo).filter(
                    Photo.organization_id == user['organization_id']
                ).order_by(Photo.uploaded_at).first()

                if oldest_photo:
                    days_active = (datetime.now() - oldest_photo.uploaded_at).days or 1
                    photos_per_day = total_photos / days_active
                    st.metric("Photos per Day (Avg)", f"{photos_per_day:.1f}")

    st.divider()

    # Recent photos
    st.markdown("### 📸 Recent Activity")

    with get_db() as db:
        recent_photos = db.query(Photo).filter(
            Photo.organization_id == user['organization_id']
        ).order_by(desc(Photo.uploaded_at)).limit(10).all()

    if recent_photos:
        for photo in recent_photos:
            with st.container():
                col1, col2, col3 = st.columns([2, 3, 3])

                with col1:
                    st.caption(photo.uploaded_at.strftime("%Y-%m-%d %I:%M %p"))

                with col2:
                    # Get person name
                    with get_db() as db:
                        person = db.query(Person).filter(Person.id == photo.person_id).first()
                        person_name = person.name if person else "Unknown"
                    st.write(f"**{person_name}**")

                with col3:
                    if photo.ai_description:
                        st.caption(f"🤖 {photo.ai_description[:50]}...")

                st.divider()
    else:
        st.info("No photos yet")

# ===== TAB 3: SETTINGS =====
with tab3:
    st.subheader("⚙️ Organization Settings")

    with st.form("org_settings_form"):
        org_name = st.text_input("Organization Name", value=org_data['name'])
        org_email = st.text_input("Contact Email", value=org_data['email'])

        submit_settings = st.form_submit_button("💾 Save Settings", use_container_width=True)

        if submit_settings:
            with get_db() as db:
                org = db.query(Organization).filter(Organization.id == user['organization_id']).first()
                if org:
                    org.name = org_name
                    org.email = org_email
                    db.commit()
                    st.success("✅ Settings updated successfully!")
                    st.rerun()

    st.divider()

    # Danger zone
    with st.expander("⚠️ Danger Zone", expanded=False):
        st.warning("**Warning:** The following actions cannot be undone!")

        if st.button("🗑️ Delete All Photos", type="secondary"):
            with get_db() as db:
                photos_deleted = db.query(Photo).filter(Photo.organization_id == user['organization_id']).delete()
                db.commit()
            st.success(f"✅ Deleted {photos_deleted} photos")
            st.rerun()

        st.caption("More administrative actions can be added here")

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>⚙️ <strong>Admin Panel</strong> - System Administration and Analytics</p>
</div>
""", unsafe_allow_html=True)
