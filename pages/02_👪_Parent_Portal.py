"""Parent Portal - View photos, children, timeline"""

import streamlit as st
from app.utils.auth import require_auth, get_current_user
from app.database import get_db
from app.database.models import Child, Photo, Activity, PhotoStatus
from datetime import datetime, timedelta
from sqlalchemy import desc
from app.utils.ui_theme import apply_professional_theme

st.set_page_config(page_title="Parent Portal", page_icon="👪", layout="wide")

# Apply professional theme
apply_professional_theme()

# Require parent authentication
require_auth(['parent'])
user = get_current_user()

st.title("👪 Parent Portal")
st.write(f"Welcome, **{user.first_name}**!")

# Get parent's children and extract data within session
with get_db() as db:
    children_db = db.query(Child).filter(Child.parent_id == user.id).all()
    # Extract all child data within the session
    children = [{
        'id': c.id,
        'first_name': c.first_name,
        'last_name': c.last_name,
        'date_of_birth': c.date_of_birth,
        'allergies': c.allergies,
        'medical_notes': c.medical_notes
    } for c in children_db]

if not children:
    st.warning("No children found. Please contact your daycare administrator to link your children.")
    st.stop()

# ===== SIDEBAR FILTERS =====
with st.sidebar:
    st.header("🔍 Filters")

    # Child selector
    child_names = {f"{child['first_name']} {child['last_name']}": child['id'] for child in children}
    selected_child_name = st.selectbox("Select Child", options=["All Children"] + list(child_names.keys()))

    # Date range
    date_range = st.date_input(
        "Date Range",
        value=(datetime.now() - timedelta(days=7), datetime.now()),
        max_value=datetime.now()
    )

    # Activity filter
    activity_types = ["All Activities", "Meal", "Nap", "Play", "Learning", "Outdoor", "Art", "Other"]
    selected_activity = st.selectbox("Activity Type", options=activity_types)

    st.divider()

    # Quick stats
    st.subheader("📊 This Week")
    with get_db() as db:
        week_ago = datetime.now() - timedelta(days=7)

        if selected_child_name != "All Children":
            child_id = child_names[selected_child_name]
            photo_count = db.query(Photo).filter(
                Photo.child_id == child_id,
                Photo.status == PhotoStatus.APPROVED,
                Photo.uploaded_at >= week_ago
            ).count()
        else:
            child_ids = [c['id'] for c in children]
            photo_count = db.query(Photo).filter(
                Photo.child_id.in_(child_ids),
                Photo.status == PhotoStatus.APPROVED,
                Photo.uploaded_at >= week_ago
            ).count()

        st.metric("New Photos", photo_count)
        st.metric("Activities", "12")  # Could calculate from activities table

# ===== MAIN CONTENT TABS =====
tab1, tab2, tab3 = st.tabs(["📸 Photos", "📅 Timeline", "👶 Children"])

# ===== TAB 1: PHOTOS =====
with tab1:
    st.subheader("📸 Photo Gallery")

    with get_db() as db:
        query = db.query(Photo).filter(Photo.status == PhotoStatus.APPROVED)

        # Apply child filter
        if selected_child_name != "All Children":
            child_id = child_names[selected_child_name]
            query = query.filter(Photo.child_id == child_id)
        else:
            child_ids = [c['id'] for c in children]
            query = query.filter(Photo.child_id.in_(child_ids))

        # Apply date filter
        if len(date_range) == 2:
            start_date, end_date = date_range
            query = query.filter(
                Photo.uploaded_at >= datetime.combine(start_date, datetime.min.time()),
                Photo.uploaded_at <= datetime.combine(end_date, datetime.max.time())
            )

        photos_db = query.order_by(desc(Photo.uploaded_at)).limit(50).all()
        # Extract photo data within session
        photos = [{
            'id': p.id,
            'url': p.url,
            'child_id': p.child_id,
            'caption': p.caption,
            'uploaded_at': p.uploaded_at
        } for p in photos_db]

    if photos:
        # Display photos in grid
        cols = st.columns(3)
        for idx, photo in enumerate(photos):
            with cols[idx % 3]:
                st.image(photo['url'], use_container_width=True)

                # Get child name
                child = next((c for c in children if c['id'] == photo['child_id']), None)
                child_name = f"{child['first_name']}" if child else "Unknown"

                st.caption(f"👶 {child_name} | {photo['uploaded_at'].strftime('%b %d, %I:%M %p')}")

                if photo['caption']:
                    st.caption(f"💬 {photo['caption']}")

                # Download button
                st.button("⬇️ Download", key=f"download_{photo['id']}", use_container_width=True)
    else:
        st.info("No photos found for the selected filters.")

# ===== TAB 2: TIMELINE =====
with tab2:
    st.subheader("📅 Daily Timeline")

    with get_db() as db:
        query = db.query(Activity)

        # Apply child filter
        if selected_child_name != "All Children":
            child_id = child_names[selected_child_name]
            query = query.filter(Activity.child_id == child_id)
        else:
            child_ids = [c['id'] for c in children]
            query = query.filter(Activity.child_id.in_(child_ids))

        # Apply date filter
        if len(date_range) == 2:
            start_date, end_date = date_range
            query = query.filter(
                Activity.activity_time >= datetime.combine(start_date, datetime.min.time()),
                Activity.activity_time <= datetime.combine(end_date, datetime.max.time())
            )

        # Apply activity type filter
        if selected_activity != "All Activities":
            query = query.filter(Activity.activity_type == selected_activity.lower())

        activities_db = query.order_by(desc(Activity.activity_time)).limit(50).all()
        # Extract activity data within session
        activities = [{
            'id': a.id,
            'child_id': a.child_id,
            'activity_type': a.activity_type,
            'activity_time': a.activity_time,
            'notes': a.notes,
            'duration_minutes': a.duration_minutes
        } for a in activities_db]

    if activities:
        # Group by date
        from itertools import groupby

        for date, day_activities in groupby(activities, key=lambda a: a['activity_time'].date()):
            st.markdown(f"### 📆 {date.strftime('%A, %B %d, %Y')}")

            for activity in day_activities:
                # Get child name
                child = next((c for c in children if c['id'] == activity['child_id']), None)
                child_name = f"{child['first_name']}" if child else "Unknown"

                # Activity icon
                icons = {
                    "meal": "🍽️",
                    "nap": "😴",
                    "play": "🎮",
                    "learning": "📚",
                    "outdoor": "🌳",
                    "art": "🎨",
                    "other": "📝"
                }
                icon = icons.get(activity['activity_type'], "📝")

                with st.container():
                    col1, col2 = st.columns([1, 5])
                    with col1:
                        st.markdown(f"**{activity['activity_time'].strftime('%I:%M %p')}**")
                    with col2:
                        st.markdown(f"{icon} **{activity['activity_type'].title()}** - {child_name}")
                        if activity['notes']:
                            st.caption(activity['notes'])
                        if activity['duration_minutes']:
                            st.caption(f"Duration: {activity['duration_minutes']} minutes")

                    st.divider()
    else:
        st.info("No activities found for the selected filters.")

# ===== TAB 3: CHILDREN =====
with tab3:
    st.subheader("👶 My Children")

    for child in children:
        with st.expander(f"👶 {child['first_name']} {child['last_name']}", expanded=True):
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
                    st.write(f"**Allergies:** {child['allergies']}")

                if child['medical_notes']:
                    st.write(f"**Medical Notes:** {child['medical_notes']}")

            with col2:
                # Quick stats for this child
                with get_db() as db:
                    week_ago = datetime.now() - timedelta(days=7)

                    photo_count = db.query(Photo).filter(
                        Photo.child_id == child['id'],
                        Photo.status == PhotoStatus.APPROVED,
                        Photo.uploaded_at >= week_ago
                    ).count()

                    activity_count = db.query(Activity).filter(
                        Activity.child_id == child['id'],
                        Activity.activity_time >= week_ago
                    ).count()

                st.metric("Photos This Week", photo_count)
                st.metric("Activities This Week", activity_count)

# ===== DAILY SUMMARY =====
st.divider()
st.subheader("📋 Today's Summary")

today = datetime.now().date()
with get_db() as db:
    if selected_child_name != "All Children":
        child_id = child_names[selected_child_name]
        today_activities_db = db.query(Activity).filter(
            Activity.child_id == child_id,
            Activity.activity_time >= datetime.combine(today, datetime.min.time())
        ).all()
    else:
        child_ids = [c['id'] for c in children]
        today_activities_db = db.query(Activity).filter(
            Activity.child_id.in_(child_ids),
            Activity.activity_time >= datetime.combine(today, datetime.min.time())
        ).all()
    # Extract today's activities within session
    today_activities = [{
        'activity_type': a.activity_type,
        'duration_minutes': a.duration_minutes
    } for a in today_activities_db]

if today_activities:
    col1, col2, col3, col4 = st.columns(4)

    meals = [a for a in today_activities if a['activity_type'] == "meal"]
    naps = [a for a in today_activities if a['activity_type'] == "nap"]

    with col1:
        st.metric("🍽️ Meals", len(meals))
    with col2:
        st.metric("😴 Naps", len(naps))
    with col3:
        total_nap_time = sum([a['duration_minutes'] or 0 for a in naps])
        st.metric("💤 Nap Time", f"{total_nap_time} min")
    with col4:
        st.metric("🎯 Activities", len(today_activities))
else:
    st.info("No activities recorded today yet.")
