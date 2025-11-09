"""Admin Panel - Manage users, daycare settings, analytics"""

import streamlit as st
from app.utils.auth import require_auth, get_current_user
from app.database import get_db
from app.database.models import User, Child, Photo, Activity, Daycare, UserRole, Subscription
from datetime import datetime, timedelta
from sqlalchemy import desc, func
import uuid
from app.utils.ui_theme import apply_professional_theme

st.set_page_config(page_title="Admin Panel", page_icon="⚙️", layout="wide")

# Apply professional theme
apply_professional_theme()

# Require admin authentication
require_auth(['admin'])
user = get_current_user()

st.title("⚙️ Admin Panel")
st.write(f"Welcome, **{user.first_name}**!")

# Get daycare info
with get_db() as db:
    daycare = db.query(Daycare).filter(Daycare.id == user.daycare_id).first()

if not daycare:
    st.error("Daycare not found!")
    st.stop()

st.info(f"Managing: **{daycare.name}**")

# ===== TABS =====
tab1, tab2, tab3, tab4, tab5 = st.tabs(["👥 Users", "👶 Children", "📊 Analytics", "⚙️ Settings", "💰 Subscription"])

# ===== TAB 1: USERS =====
with tab1:
    st.subheader("👥 User Management")

    # Add new user section
    with st.expander("➕ Add New User", expanded=False):
        with st.form("add_user_form"):
            col1, col2 = st.columns(2)

            with col1:
                new_first_name = st.text_input("First Name")
                new_email = st.text_input("Email")
                new_password = st.text_input("Temporary Password", type="password")

            with col2:
                new_last_name = st.text_input("Last Name")
                new_phone = st.text_input("Phone (optional)")
                new_role = st.selectbox("Role", options=["Parent", "Staff", "Admin"])

            submit_user = st.form_submit_button("➕ Add User", use_container_width=True)

            if submit_user:
                if not all([new_first_name, new_last_name, new_email, new_password]):
                    st.error("Please fill in all required fields")
                else:
                    from app.utils.auth import register_user

                    new_user, error = register_user(
                        email=new_email,
                        password=new_password,
                        first_name=new_first_name,
                        last_name=new_last_name,
                        role=new_role.lower(),
                        daycare_id=user.daycare_id,
                        phone=new_phone
                    )

                    if new_user:
                        st.success(f"✅ User {new_email} created successfully!")
                        st.rerun()
                    else:
                        st.error(f"❌ Error: {error}")

    st.divider()

    # List existing users
    st.subheader("📋 Existing Users")

    with get_db() as db:
        users = db.query(User).filter(User.daycare_id == user.daycare_id).order_by(User.role, User.last_name).all()

    # Group users by role
    parents = [u for u in users if u.role == UserRole.PARENT]
    staff = [u for u in users if u.role == UserRole.STAFF]
    admins = [u for u in users if u.role == UserRole.ADMIN]

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("👪 Parents", len(parents))
    with col2:
        st.metric("👨‍🏫 Staff", len(staff))
    with col3:
        st.metric("⚙️ Admins", len(admins))

    # Display users by role
    for role_name, role_users in [("Admins", admins), ("Staff", staff), ("Parents", parents)]:
        if role_users:
            st.markdown(f"### {role_name}")

            for usr in role_users:
                with st.expander(f"{usr.first_name} {usr.last_name} ({usr.email})"):
                    col1, col2 = st.columns(2)

                    with col1:
                        st.write(f"**Email:** {usr.email}")
                        st.write(f"**Phone:** {usr.phone or 'N/A'}")
                        st.write(f"**Role:** {usr.role.value}")
                        st.write(f"**Created:** {usr.created_at.strftime('%b %d, %Y')}")
                        if usr.last_login:
                            st.write(f"**Last Login:** {usr.last_login.strftime('%b %d, %Y %I:%M %p')}")

                    with col2:
                        if usr.role == UserRole.PARENT:
                            # Show linked children
                            with get_db() as db:
                                children = db.query(Child).filter(Child.parent_id == usr.id).all()

                            if children:
                                st.write("**Children:**")
                                for child in children:
                                    st.write(f"- {child.first_name} {child.last_name}")
                            else:
                                st.info("No children linked")

                        # Action buttons
                        if usr.id != user.id:  # Don't allow deleting self
                            if st.button(f"🗑️ Delete User", key=f"delete_{usr.id}"):
                                with get_db() as db:
                                    user_to_delete = db.query(User).filter(User.id == usr.id).first()
                                    db.delete(user_to_delete)
                                st.warning("User deleted!")
                                st.rerun()

# ===== TAB 2: CHILDREN =====
with tab2:
    st.subheader("👶 Children Management")

    # Add new child
    with st.expander("➕ Add New Child", expanded=False):
        with st.form("add_child_form"):
            col1, col2 = st.columns(2)

            with col1:
                child_first_name = st.text_input("First Name")
                child_last_name = st.text_input("Last Name")
                child_dob = st.date_input("Date of Birth", max_value=datetime.now())

            with col2:
                # Select parent
                with get_db() as db:
                    parents = db.query(User).filter(
                        User.daycare_id == user.daycare_id,
                        User.role == UserRole.PARENT
                    ).all()

                parent_options = {f"{p.first_name} {p.last_name} ({p.email})": p.id for p in parents}
                selected_parent = st.selectbox("Parent", options=list(parent_options.keys()) if parent_options else ["No parents available"])

                child_allergies = st.text_area("Allergies (if any)")
                child_medical = st.text_area("Medical Notes")

            submit_child = st.form_submit_button("➕ Add Child", use_container_width=True)

            if submit_child:
                if not all([child_first_name, child_last_name, child_dob]) or not parent_options:
                    st.error("Please fill in all required fields and ensure parents exist")
                else:
                    parent_id = parent_options[selected_parent]

                    with get_db() as db:
                        new_child = Child(
                            id=str(uuid.uuid4()),
                            first_name=child_first_name,
                            last_name=child_last_name,
                            date_of_birth=child_dob,
                            parent_id=parent_id,
                            daycare_id=user.daycare_id,
                            allergies=child_allergies if child_allergies else None,
                            medical_notes=child_medical if child_medical else None,
                            created_at=datetime.utcnow()
                        )
                        db.add(new_child)

                    st.success(f"✅ Child {child_first_name} added successfully!")
                    st.rerun()

    st.divider()

    # List existing children
    st.subheader("📋 All Children")

    with get_db() as db:
        children = db.query(Child).filter(Child.daycare_id == user.daycare_id).order_by(Child.last_name).all()

    st.metric("👶 Total Children", len(children))

    if children:
        for child in children:
            with st.expander(f"👶 {child.first_name} {child.last_name}"):
                col1, col2 = st.columns(2)

                with col1:
                    st.write(f"**Birthday:** {child.date_of_birth.strftime('%B %d, %Y')}")

                    # Calculate age
                    today = datetime.now().date()
                    age_years = today.year - child.date_of_birth.year
                    st.write(f"**Age:** {age_years} years")

                    if child.allergies:
                        st.warning(f"⚠️ **Allergies:** {child.allergies}")

                    if child.medical_notes:
                        st.info(f"🏥 **Medical Notes:** {child.medical_notes}")

                with col2:
                    # Parent info
                    if child.parent_id:
                        with get_db() as db:
                            parent = db.query(User).filter(User.id == child.parent_id).first()

                        if parent:
                            st.write(f"**Parent:** {parent.first_name} {parent.last_name}")
                            st.write(f"**Email:** {parent.email}")

                    # Delete button
                    if st.button(f"🗑️ Delete Child", key=f"delete_child_{child.id}"):
                        with get_db() as db:
                            child_to_delete = db.query(Child).filter(Child.id == child.id).first()
                            db.delete(child_to_delete)
                        st.warning("Child removed!")
                        st.rerun()

# ===== TAB 3: ANALYTICS =====
with tab3:
    st.subheader("📊 Analytics & Reports")

    # Date range selector
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("From", value=datetime.now() - timedelta(days=30))
    with col2:
        end_date = st.date_input("To", value=datetime.now())

    st.divider()

    # Overall metrics
    with get_db() as db:
        # Photos
        total_photos = db.query(Photo).filter(
            Photo.daycare_id == user.daycare_id,
            Photo.uploaded_at >= datetime.combine(start_date, datetime.min.time()),
            Photo.uploaded_at <= datetime.combine(end_date, datetime.max.time())
        ).count()

        # Activities
        total_activities = db.query(Activity).filter(
            Activity.daycare_id == user.daycare_id,
            Activity.activity_time >= datetime.combine(start_date, datetime.min.time()),
            Activity.activity_time <= datetime.combine(end_date, datetime.max.time())
        ).count()

        # Active users (logged in during period)
        active_users = db.query(User).filter(
            User.daycare_id == user.daycare_id,
            User.last_login >= datetime.combine(start_date, datetime.min.time())
        ).count()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📸 Total Photos", total_photos)
    with col2:
        st.metric("📝 Total Activities", total_activities)
    with col3:
        st.metric("👥 Active Users", active_users)
    with col4:
        avg_photos_per_day = total_photos / max((end_date - start_date).days, 1)
        st.metric("📊 Avg Photos/Day", f"{avg_photos_per_day:.1f}")

    st.divider()

    # Activity breakdown
    st.subheader("📊 Activity Breakdown")

    with get_db() as db:
        activity_counts = db.query(
            Activity.activity_type,
            func.count(Activity.id).label('count')
        ).filter(
            Activity.daycare_id == user.daycare_id,
            Activity.activity_time >= datetime.combine(start_date, datetime.min.time()),
            Activity.activity_time <= datetime.combine(end_date, datetime.max.time())
        ).group_by(Activity.activity_type).all()

    if activity_counts:
        for activity_type, count in activity_counts:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**{activity_type.title()}**")
            with col2:
                st.write(f"{count}")
    else:
        st.info("No activity data for selected period")

    st.divider()

    # Most active staff
    st.subheader("👨‍🏫 Most Active Staff")

    with get_db() as db:
        staff_activity = db.query(
            Activity.staff_id,
            func.count(Activity.id).label('count')
        ).filter(
            Activity.daycare_id == user.daycare_id,
            Activity.activity_time >= datetime.combine(start_date, datetime.min.time()),
            Activity.activity_time <= datetime.combine(end_date, datetime.max.time())
        ).group_by(Activity.staff_id).order_by(desc('count')).limit(5).all()

        for staff_id, count in staff_activity:
            staff_member = db.query(User).filter(User.id == staff_id).first()
            if staff_member:
                st.write(f"**{staff_member.first_name} {staff_member.last_name}:** {count} activities")

# ===== TAB 4: SETTINGS =====
with tab4:
    st.subheader("⚙️ Daycare Settings")

    with st.form("daycare_settings_form"):
        daycare_name = st.text_input("Daycare Name", value=daycare.name)
        daycare_email = st.text_input("Contact Email", value=daycare.email)
        daycare_phone = st.text_input("Phone", value=daycare.phone or "")
        daycare_address = st.text_area("Address", value=daycare.address or "")
        daycare_license = st.text_input("License Number", value=daycare.license_number or "")

        st.divider()

        st.subheader("📸 Photo Settings")
        auto_approve_photos = st.checkbox("Auto-approve all photos", value=False)
        enable_face_recognition = st.checkbox("Enable face recognition", value=True)
        photo_retention_days = st.number_input("Photo retention (days, 0 = forever)", min_value=0, value=0)

        st.divider()

        st.subheader("🔔 Notification Settings")
        notify_parents_new_photos = st.checkbox("Notify parents of new photos", value=True)
        notify_parents_activities = st.checkbox("Notify parents of new activities", value=True)
        notification_method = st.multiselect(
            "Notification methods",
            options=["Email", "SMS", "Push"],
            default=["Email"]
        )

        submit_settings = st.form_submit_button("💾 Save Settings", use_container_width=True)

        if submit_settings:
            with get_db() as db:
                daycare_to_update = db.query(Daycare).filter(Daycare.id == user.daycare_id).first()
                daycare_to_update.name = daycare_name
                daycare_to_update.email = daycare_email
                daycare_to_update.phone = daycare_phone
                daycare_to_update.address = daycare_address
                daycare_to_update.license_number = daycare_license

            st.success("✅ Settings saved successfully!")

# ===== TAB 5: SUBSCRIPTION =====
with tab5:
    st.subheader("💰 Subscription & Billing")

    with get_db() as db:
        subscription = db.query(Subscription).filter(Subscription.daycare_id == user.daycare_id).first()

    if subscription:
        st.write(f"**Current Plan:** {subscription.plan_name}")
        st.write(f"**Status:** {subscription.status}")
        st.write(f"**Billing Cycle:** {subscription.billing_cycle}")
        st.write(f"**Price:** ${subscription.price}/month")

        if subscription.trial_end_date:
            st.info(f"Trial ends: {subscription.trial_end_date.strftime('%B %d, %Y')}")

        if subscription.next_billing_date:
            st.write(f"**Next Billing:** {subscription.next_billing_date.strftime('%B %d, %Y')}")

        # Usage stats
        st.divider()
        st.subheader("📊 Usage This Month")

        current_month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0)

        with get_db() as db:
            photos_this_month = db.query(Photo).filter(
                Photo.daycare_id == user.daycare_id,
                Photo.uploaded_at >= current_month_start
            ).count()

            storage_used_mb = 0  # Would calculate actual storage in production

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Photos Uploaded", photos_this_month)
        with col2:
            st.metric("Storage Used", f"{storage_used_mb} MB")
        with col3:
            st.metric("Active Users", len(users))

        st.divider()

        # Upgrade/manage
        if st.button("🚀 Upgrade Plan", use_container_width=True):
            st.info("Redirecting to pricing page...")
            st.switch_page("pages/07_💰_Pricing.py")

    else:
        st.warning("No active subscription found!")
        st.info("Please visit the pricing page to subscribe.")
        if st.button("View Pricing Plans", use_container_width=True):
            st.switch_page("pages/07_💰_Pricing.py")
