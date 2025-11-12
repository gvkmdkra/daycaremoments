"""
Parent Portal - View photos with AI descriptions, activities timeline, and daily summaries
Shows only photos of parent's children with AI-generated descriptions
"""

import streamlit as st
from app.utils.auth import require_auth, get_current_user
from app.database import get_db
from app.database.models import Child, Photo, Activity, PhotoStatus
from datetime import datetime, timedelta, date
from sqlalchemy import desc, and_
from app.utils.ui_theme import apply_professional_theme
from app.services.llm_service import get_llm_service
from itertools import groupby

st.set_page_config(page_title="Parent Portal", page_icon="👪", layout="wide")

# Apply professional theme
apply_professional_theme()

# Require parent authentication
require_auth(['parent'])
user = get_current_user()

st.title("👪 Parent Portal")
st.write(f"Welcome, **{user.first_name}**! View your child's daily moments.")

# Get parent's children
with get_db() as db:
    children_db = db.query(Child).join(
        Child.parents
    ).filter(
        Child.parents.any(id=user.id),
        Child.is_active == True
    ).all()

    # Extract child data
    children = [{
        'id': c.id,
        'first_name': c.first_name,
        'last_name': c.last_name,
        'date_of_birth': c.date_of_birth,
        'allergies': c.allergies,
        'medical_notes': c.medical_notes,
        'training_photo_count': c.training_photo_count
    } for c in children_db]

if not children:
    st.warning("👶 No children linked to your account. Please contact your daycare administrator.")
    st.stop()

# ===== SIDEBAR FILTERS =====
with st.sidebar:
    st.header("🔍 Filters")

    # Child selector
    child_names = {f"{child['first_name']} {child['last_name']}": child['id'] for child in children}
    selected_child_name = st.selectbox(
        "Select Child",
        options=["All Children"] + list(child_names.keys()),
        help="Filter by child"
    )

    # Date range
    date_options = {
        "Today": (date.today(), date.today()),
        "This Week": (date.today() - timedelta(days=7), date.today()),
        "This Month": (date.today() - timedelta(days=30), date.today()),
        "Custom Range": None
    }

    date_selection = st.selectbox("Date Range", options=list(date_options.keys()))

    if date_selection == "Custom Range":
        date_range = st.date_input(
            "Select dates",
            value=(datetime.now() - timedelta(days=7), datetime.now()),
            max_value=datetime.now()
        )
    else:
        date_range = date_options[date_selection]

    # Activity filter
    activity_types = ["All Activities", "Meal", "Nap", "Play", "Learning", "Outdoor", "Art", "Other"]
    selected_activity = st.selectbox("Activity Type", options=activity_types)

    st.divider()

    # Quick stats
    st.subheader("📊 Quick Stats")

    child_ids = [c['id'] for c in children]

    if selected_child_name != "All Children":
        selected_child_ids = [child_names[selected_child_name]]
    else:
        selected_child_ids = child_ids

    with get_db() as db:
        week_ago = datetime.now() - timedelta(days=7)

        photo_count = db.query(Photo).filter(
            Photo.child_id.in_(selected_child_ids),
            Photo.status == PhotoStatus.APPROVED,
            Photo.uploaded_at >= week_ago
        ).count()

        activity_count = db.query(Activity).filter(
            Activity.child_id.in_(selected_child_ids),
            Activity.activity_time >= week_ago
        ).count()

        auto_tagged = db.query(Photo).filter(
            Photo.child_id.in_(selected_child_ids),
            Photo.status == PhotoStatus.APPROVED,
            Photo.uploaded_at >= week_ago,
            Photo.auto_tagged == True
        ).count()

    st.metric("Photos This Week", photo_count)
    st.metric("Activities Logged", activity_count)
    st.metric("🤖 AI Auto-Tagged", auto_tagged)

# ===== MAIN CONTENT TABS =====
tab1, tab2, tab3, tab4 = st.tabs(["📸 Photo Gallery", "📅 Daily Timeline", "📋 Daily Summary", "👶 My Children"])

# ===== TAB 1: PHOTO GALLERY WITH AI DESCRIPTIONS =====
with tab1:
    st.subheader("📸 Photo Gallery")

    with get_db() as db:
        query = db.query(Photo).filter(
            Photo.status == PhotoStatus.APPROVED,
            Photo.child_id.in_(selected_child_ids)
        )

        # Apply date filter
        if len(date_range) == 2:
            start_date, end_date = date_range
            query = query.filter(
                Photo.uploaded_at >= datetime.combine(start_date, datetime.min.time()),
                Photo.uploaded_at <= datetime.combine(end_date, datetime.max.time())
            )

        # Apply activity filter
        if selected_activity != "All Activities":
            query = query.join(Photo.activity).filter(
                Activity.activity_type == selected_activity.lower()
            )

        photos_db = query.order_by(desc(Photo.uploaded_at)).limit(50).all()

        # Extract photo data with child and activity info
        photos = []
        for p in photos_db:
            child = next((c for c in children if c['id'] == p.child_id), None)

            photos.append({
                'id': p.id,
                'url': p.url,
                'child_id': p.child_id,
                'child_name': f"{child['first_name']} {child['last_name']}" if child else "Unknown",
                'caption': p.caption,
                'ai_description': p.ai_generated_description,
                'auto_tagged': p.auto_tagged,
                'uploaded_at': p.uploaded_at,
                'activity_type': p.activity.activity_type if p.activity else None,
                'activity_mood': p.activity.mood if p.activity else None
            })

    if photos:
        st.info(f"📷 Showing {len(photos)} photo(s)")

        # Group photos by date
        photos_by_date = {}
        for photo in photos:
            photo_date = photo['uploaded_at'].date()
            if photo_date not in photos_by_date:
                photos_by_date[photo_date] = []
            photos_by_date[photo_date].append(photo)

        # Display photos grouped by date
        for photo_date in sorted(photos_by_date.keys(), reverse=True):
            st.markdown(f"### 📅 {photo_date.strftime('%A, %B %d, %Y')}")

            day_photos = photos_by_date[photo_date]

            # Display in 3-column grid
            cols = st.columns(3)
            for idx, photo in enumerate(day_photos):
                with cols[idx % 3]:
                    # Photo card
                    with st.container():
                        st.image(photo['url'], use_container_width=True)

                        # Activity badge
                        if photo['activity_type']:
                            activity_icons = {
                                "meal": "🍽️",
                                "nap": "😴",
                                "play": "🎮",
                                "learning": "📚",
                                "outdoor": "🌳",
                                "art": "🎨",
                                "other": "📝"
                            }
                            icon = activity_icons.get(photo['activity_type'], "📝")
                            st.markdown(f"{icon} **{photo['activity_type'].title()}**")

                        # Child name
                        st.markdown(f"**👶 {photo['child_name']}**")

                        # AI-generated description (highlighted)
                        if photo['ai_description']:
                            st.info(f"🤖 {photo['ai_description']}")
                        elif photo['caption']:
                            st.caption(f"💬 {photo['caption']}")

                        # Timestamp
                        st.caption(f"📅 {photo['uploaded_at'].strftime('%I:%M %p')}")

                        # Auto-tagged badge
                        if photo['auto_tagged']:
                            st.caption("✨ AI Auto-Tagged")

                        # Mood indicator
                        if photo['activity_mood']:
                            mood_emojis = {
                                "happy": "😊",
                                "calm": "😌",
                                "focused": "🤔",
                                "sleepy": "😴",
                                "excited": "🤗",
                                "curious": "🧐"
                            }
                            mood_emoji = mood_emojis.get(photo['activity_mood'], "😊")
                            st.caption(f"Mood: {mood_emoji} {photo['activity_mood'].title()}")

                    st.markdown("---")

            st.divider()

    else:
        st.info("📷 No photos found. Try adjusting your filters or check back later!")

# ===== TAB 2: DAILY TIMELINE =====
with tab2:
    st.subheader("📅 Daily Activity Timeline")

    with get_db() as db:
        query = db.query(Activity).filter(
            Activity.child_id.in_(selected_child_ids)
        )

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

        # Extract activity data
        activities = []
        for a in activities_db:
            child = next((c for c in children if c['id'] == a.child_id), None)

            activities.append({
                'id': a.id,
                'child_id': a.child_id,
                'child_name': f"{child['first_name']}" if child else "Unknown",
                'activity_type': a.activity_type,
                'activity_time': a.activity_time,
                'notes': a.notes,
                'duration_minutes': a.duration_minutes,
                'mood': a.mood
            })

    if activities:
        # Group by date
        activities_by_date = {}
        for activity in activities:
            activity_date = activity['activity_time'].date()
            if activity_date not in activities_by_date:
                activities_by_date[activity_date] = []
            activities_by_date[activity_date].append(activity)

        for activity_date in sorted(activities_by_date.keys(), reverse=True):
            st.markdown(f"### 📆 {activity_date.strftime('%A, %B %d, %Y')}")

            day_activities = activities_by_date[activity_date]

            for activity in day_activities:
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
                        st.markdown(f"{icon} **{activity['activity_type'].title()}** - {activity['child_name']}")

                        if activity['notes']:
                            st.info(activity['notes'])

                        col_a, col_b = st.columns(2)
                        with col_a:
                            if activity['duration_minutes']:
                                st.caption(f"⏱️ Duration: {activity['duration_minutes']} minutes")

                        with col_b:
                            if activity['mood']:
                                mood_emojis = {
                                    "happy": "😊", "calm": "😌", "focused": "🤔",
                                    "sleepy": "😴", "excited": "🤗", "curious": "🧐"
                                }
                                mood_emoji = mood_emojis.get(activity['mood'], "😊")
                                st.caption(f"Mood: {mood_emoji} {activity['mood'].title()}")

                st.divider()

            st.markdown("---")

    else:
        st.info("📅 No activities found for the selected period.")

# ===== TAB 3: AI-GENERATED DAILY SUMMARY =====
with tab3:
    st.subheader("📋 AI-Generated Daily Summary")

    # Date selector for summary
    summary_date = st.date_input(
        "Select Date",
        value=date.today(),
        max_value=date.today()
    )

    if st.button("📝 Generate Summary", type="primary"):
        with st.spinner("🤖 Generating personalized daily summary..."):
            with get_db() as db:
                # Get activities for the day
                day_activities = db.query(Activity).filter(
                    Activity.child_id.in_(selected_child_ids),
                    Activity.activity_time >= datetime.combine(summary_date, datetime.min.time()),
                    Activity.activity_time <= datetime.combine(summary_date, datetime.max.time())
                ).all()

                # Get photos for the day
                day_photos = db.query(Photo).filter(
                    Photo.child_id.in_(selected_child_ids),
                    Photo.status == PhotoStatus.APPROVED,
                    Photo.uploaded_at >= datetime.combine(summary_date, datetime.min.time()),
                    Photo.uploaded_at <= datetime.combine(summary_date, datetime.max.time())
                ).count()

                if day_activities or day_photos:
                    # Prepare activity data
                    activity_data = [{
                        'activity_type': a.activity_type,
                        'notes': a.notes,
                        'time': a.activity_time.strftime('%I:%M %p')
                    } for a in day_activities]

                    # Generate summary for each child
                    llm_service = get_llm_service()

                    for child in children:
                        if selected_child_name != "All Children" and child['id'] != child_names[selected_child_name]:
                            continue

                        child_activities = [a for a in activity_data if any(
                            act.child_id == child['id'] for act in day_activities
                        )]

                        if child_activities:
                            summary = llm_service.generate_daily_summary(
                                child_name=child['first_name'],
                                activities=child_activities,
                                photo_count=day_photos
                            )

                            st.markdown(f"### 👶 {child['first_name']} {child['last_name']}")
                            st.success(summary)

                            # Activity breakdown
                            with st.expander("📊 Activity Breakdown"):
                                activity_counts = {}
                                for act in day_activities:
                                    if act.child_id == child['id']:
                                        activity_counts[act.activity_type] = activity_counts.get(act.activity_type, 0) + 1

                                cols = st.columns(len(activity_counts))
                                for idx, (act_type, count) in enumerate(activity_counts.items()):
                                    with cols[idx]:
                                        st.metric(act_type.title(), count)

                            st.divider()
                else:
                    st.info("No activities or photos recorded for this date.")

    # Show existing summaries section
    st.divider()
    st.markdown("### 📚 Recent Daily Summaries")

    with get_db() as db:
        # Get recent activities with AI-generated notes
        recent_dates = db.query(Activity.activity_time).filter(
            Activity.child_id.in_(selected_child_ids),
            Activity.notes.isnot(None)
        ).distinct().order_by(desc(Activity.activity_time)).limit(5).all()

        for date_tuple in recent_dates:
            activity_date = date_tuple[0].date()

            with st.expander(f"📅 {activity_date.strftime('%A, %B %d, %Y')}"):
                date_activities = db.query(Activity).filter(
                    Activity.child_id.in_(selected_child_ids),
                    Activity.activity_time >= datetime.combine(activity_date, datetime.min.time()),
                    Activity.activity_time <= datetime.combine(activity_date, datetime.max.time())
                ).all()

                for activity in date_activities:
                    if activity.notes:
                        child = next((c for c in children if c['id'] == activity.child_id), None)
                        st.write(f"**{activity.activity_time.strftime('%I:%M %p')}** - {activity.activity_type.title()}")
                        st.info(activity.notes)

# ===== TAB 4: CHILDREN INFORMATION =====
with tab4:
    st.subheader("👶 My Children")

    for child in children:
        with st.expander(f"👶 {child['first_name']} {child['last_name']}", expanded=True):
            col1, col2 = st.columns(2)

            with col1:
                st.write(f"**Birthday:** {child['date_of_birth'].strftime('%B %d, %Y')}")

                # Calculate age
                today = date.today()
                age_years = today.year - child['date_of_birth'].year
                age_months = today.month - child['date_of_birth'].month
                if age_months < 0:
                    age_years -= 1
                    age_months += 12

                st.write(f"**Age:** {age_years} years, {age_months} months")

                if child['allergies']:
                    st.warning(f"⚠️ **Allergies:** {child['allergies']}")

                if child['medical_notes']:
                    st.info(f"📋 **Medical Notes:** {child['medical_notes']}")

                # Face recognition status
                if child['training_photo_count'] >= 3:
                    st.success(f"✅ Face Recognition Active ({child['training_photo_count']} training photos)")
                else:
                    st.warning("⚠️ Face Recognition Not Active")

            with col2:
                # Stats for this child
                with get_db() as db:
                    week_ago = datetime.now() - timedelta(days=7)
                    month_ago = datetime.now() - timedelta(days=30)

                    week_photos = db.query(Photo).filter(
                        Photo.child_id == child['id'],
                        Photo.status == PhotoStatus.APPROVED,
                        Photo.uploaded_at >= week_ago
                    ).count()

                    month_photos = db.query(Photo).filter(
                        Photo.child_id == child['id'],
                        Photo.status == PhotoStatus.APPROVED,
                        Photo.uploaded_at >= month_ago
                    ).count()

                    week_activities = db.query(Activity).filter(
                        Activity.child_id == child['id'],
                        Activity.activity_time >= week_ago
                    ).count()

                st.metric("Photos This Week", week_photos)
                st.metric("Photos This Month", month_photos)
                st.metric("Activities This Week", week_activities)

# ===== FOOTER INFO =====
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>🤖 <strong>Powered by AI</strong> - Automatic face recognition and activity descriptions</p>
    <p>Photos and activities are updated in real-time by your daycare staff</p>
</div>
""", unsafe_allow_html=True)
