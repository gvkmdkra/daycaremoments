"""
Parent Portal - View photos with AI descriptions
Shows only photos of parent's children with AI-generated descriptions
"""

import streamlit as st
from app.utils.auth import require_auth, get_current_user
from app.database import get_db
from app.database.models import Person, Photo
from datetime import datetime, timedelta, date
from sqlalchemy import desc

st.set_page_config(page_title="Parent Portal", page_icon="👪", layout="wide")

# Require parent authentication
require_auth(['parent'])
user = get_current_user()

st.title("👪 Parent Portal")
st.write(f"Welcome, **{user['email']}**! View your child's daily moments.")

# Get parent's children (persons in their organization)
with get_db() as db:
    persons_db = db.query(Person).filter(
        Person.organization_id == user['organization_id']
    ).all()

    # Extract person data
    persons = [{
        'id': p.id,
        'name': p.name,
        'organization_id': p.organization_id
    } for p in persons_db]

if not persons:
    st.warning("👶 No children linked to your organization. Please contact your daycare administrator.")
    st.stop()

# ===== SIDEBAR FILTERS =====
with st.sidebar:
    st.header("🔍 Filters")

    # Person selector
    person_names = {person['name']: person['id'] for person in persons}
    selected_person_name = st.selectbox(
        "Select Child",
        options=["All Children"] + list(person_names.keys()),
        help="Filter by child"
    )

    # Date range
    date_options = {
        "Today": (date.today(), date.today()),
        "This Week": (date.today() - timedelta(days=7), date.today()),
        "This Month": (date.today() - timedelta(days=30), date.today()),
        "Custom Range": None
    }

    date_selection = st.selectbox("Date Range", options=list(date_options.keys()), index=1)  # Default to "This Week"

    if date_selection == "Custom Range":
        date_range = st.date_input(
            "Select dates",
            value=(datetime.now() - timedelta(days=7), datetime.now()),
            max_value=datetime.now()
        )
    else:
        date_range = date_options[date_selection]

    st.divider()

    # Quick stats
    st.subheader("📊 Quick Stats")

    person_ids = [p['id'] for p in persons]

    if selected_person_name != "All Children":
        selected_person_ids = [person_names[selected_person_name]]
    else:
        selected_person_ids = person_ids

    with get_db() as db:
        week_ago = datetime.now() - timedelta(days=7)

        photo_count = db.query(Photo).filter(
            Photo.person_id.in_(selected_person_ids),
            Photo.uploaded_at >= week_ago
        ).count()

        ai_described = db.query(Photo).filter(
            Photo.person_id.in_(selected_person_ids),
            Photo.uploaded_at >= week_ago,
            Photo.ai_description.isnot(None)
        ).count()

    st.metric("Photos This Week", photo_count)
    st.metric("🤖 AI Described", ai_described)

# ===== MAIN CONTENT TABS =====
tab1, tab2 = st.tabs(["📸 Photo Gallery", "👶 My Children"])

# ===== TAB 1: PHOTO GALLERY WITH AI DESCRIPTIONS =====
with tab1:
    st.subheader("📸 Photo Gallery")

    with get_db() as db:
        query = db.query(Photo).filter(
            Photo.person_id.in_(selected_person_ids)
        )

        # Apply date filter
        if date_range and len(date_range) == 2:
            start_date, end_date = date_range
            query = query.filter(
                Photo.uploaded_at >= datetime.combine(start_date, datetime.min.time()),
                Photo.uploaded_at <= datetime.combine(end_date, datetime.max.time())
            )

        photos_db = query.order_by(desc(Photo.uploaded_at)).limit(50).all()

        # Extract photo data with person info
        photos = []
        for p in photos_db:
            person = next((per for per in persons if per['id'] == p.person_id), None)

            photos.append({
                'id': p.id,
                'url': p.url,
                'person_id': p.person_id,
                'person_name': person['name'] if person else "Unknown",
                'ai_description': p.ai_description,
                'uploaded_at': p.uploaded_at
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
                        # Display placeholder image (in production, this would be real photos)
                        st.markdown(f"""
                        <div style="
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            height: 250px;
                            border-radius: 10px;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            color: white;
                            font-size: 1.2rem;
                            font-weight: 600;
                            margin-bottom: 1rem;
                        ">
                            📸 {photo['person_name']}
                        </div>
                        """, unsafe_allow_html=True)

                        # Child name
                        st.markdown(f"**👶 {photo['person_name']}**")

                        # AI-generated description (highlighted)
                        if photo['ai_description']:
                            st.info(f"🤖 {photo['ai_description']}")
                        else:
                            st.caption("No AI description yet")

                        # Timestamp
                        st.caption(f"📅 {photo['uploaded_at'].strftime('%I:%M %p')}")

                    st.markdown("---")

            st.divider()

    else:
        st.info("📷 No photos found. Try adjusting your filters or check back later!")

# ===== TAB 2: CHILDREN INFORMATION =====
with tab2:
    st.subheader("👶 My Children")

    for person in persons:
        with st.expander(f"👶 {person['name']}", expanded=True):
            col1, col2 = st.columns(2)

            with col1:
                st.write(f"**Name:** {person['name']}")
                st.write(f"**Organization:** {user['organization_id']}")

            with col2:
                # Stats for this person
                with get_db() as db:
                    week_ago = datetime.now() - timedelta(days=7)
                    month_ago = datetime.now() - timedelta(days=30)

                    week_photos = db.query(Photo).filter(
                        Photo.person_id == person['id'],
                        Photo.uploaded_at >= week_ago
                    ).count()

                    month_photos = db.query(Photo).filter(
                        Photo.person_id == person['id'],
                        Photo.uploaded_at >= month_ago
                    ).count()

                st.metric("Photos This Week", week_photos)
                st.metric("Photos This Month", month_photos)

# ===== FOOTER INFO =====
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>🤖 <strong>Powered by AI</strong> - Automatic face recognition and activity descriptions</p>
    <p>Photos are updated in real-time by your daycare staff</p>
</div>
""", unsafe_allow_html=True)
