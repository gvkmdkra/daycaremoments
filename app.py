"""
DaycareMoments - Main Application Entry Point
AI-Powered Photo Sharing for Daycares
"""

import streamlit as st
from app.database import init_db
from app.utils.ui_theme import apply_professional_theme, create_feature_card, create_metric_card

# Page config
st.set_page_config(
    page_title="DaycareMoments - AI-Powered Daycare Photo Sharing",
    page_icon="👶",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://daycaremoments.com/help',
        'Report a bug': 'https://github.com/daycaremoments/issues',
        'About': "# DaycareMoments\nAI-Powered Photo Sharing Platform for Daycares"
    }
)

# Initialize database
try:
    init_db()
except Exception as e:
    st.error(f"Database initialization error: {e}")
    st.stop()

# Apply professional theme
apply_professional_theme()

# Header
st.markdown('<h1 style="text-align: center;">👶 DaycareMoments</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; font-size: 1.2rem; color: white; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">AI-Powered Photo Sharing Platform for Daycares</p>', unsafe_allow_html=True)

# Check if user is logged in
if 'user_id' in st.session_state:
    st.success(f"✅ Welcome back, {st.session_state.get('first_name', 'User')}!")
    st.info("👈 Use the sidebar to navigate to your dashboard")
else:
    st.info("👈 Please login or register using the sidebar to get started")

st.divider()

# Feature highlights
st.subheader("✨ Key Features")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(create_feature_card(
        "📸",
        "Smart Photo Sharing",
        "Upload photos with automatic face recognition. Children are tagged instantly using AI."
    ), unsafe_allow_html=True)

with col2:
    st.markdown(create_feature_card(
        "💬",
        "AI Assistant",
        "Chat with AI to find photos, get daily summaries, and answer questions about your child's day."
    ), unsafe_allow_html=True)

with col3:
    st.markdown(create_feature_card(
        "📞",
        "Voice Calling",
        "Call our 24/7 AI agent to hear about your child's activities and request photos via phone."
    ), unsafe_allow_html=True)

st.divider()

# Stats (demo data)
st.subheader("📊 Platform Statistics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="📸 Total Photos",
        value="12,450",
        delta="+1,234 this month"
    )

with col2:
    st.metric(
        label="🏫 Active Daycares",
        value="45",
        delta="+3 this month"
    )

with col3:
    st.metric(
        label="👨‍👩‍👧‍👦 Happy Parents",
        value="892",
        delta="+67 this month"
    )

with col4:
    st.metric(
        label="👶 Children",
        value="1,234",
        delta="+45 this month"
    )

st.divider()

# How it works
st.subheader("🔄 How It Works")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### For Parents 👨‍👩‍👧‍👦
    1. **Login** to your account
    2. **View** your child's daily photos
    3. **Chat** with AI about their activities
    4. **Receive** notifications instantly
    5. **Download** photos to keep forever
    """)

with col2:
    st.markdown("""
    ### For Staff 👨‍🏫
    1. **Upload** photos throughout the day
    2. **Auto-tag** children with AI face recognition
    3. **Approve** photos before sharing
    4. **Manage** activities and schedules
    5. **View** analytics and reports
    """)

st.divider()

# Pricing preview
st.subheader("💰 Pricing Plans")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    ### Free
    - 50 children
    - 100 photos/month
    - Email notifications
    - 20 AI queries/day

    **$0/month**
    """)

with col2:
    st.markdown("""
    ### Starter ⭐
    - 100 children
    - 500 photos/month
    - Email + SMS
    - 100 AI queries/day
    - Voice calling

    **$29/month**
    """)

with col3:
    st.markdown("""
    ### Professional 🚀
    - Unlimited children
    - Unlimited photos
    - All notifications
    - Unlimited AI
    - Priority support

    **$99/month**
    """)

st.divider()

# Footer
st.markdown("""
<div style="text-align: center; padding: 2rem; color: #666;">
    <p>Made with ❤️ for daycares and parents everywhere</p>
    <p style="font-size: 0.9rem;">© 2025 DaycareMoments | Privacy Policy | Terms of Service</p>
</div>
""", unsafe_allow_html=True)
