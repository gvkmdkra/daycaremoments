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

# Simple, Professional Hero Section
st.markdown("""
<div style="text-align: center; padding: 2rem 1rem; max-width: 900px; margin: 0 auto;">
    <h1 style="font-size: clamp(2rem, 5vw, 3.5rem); color: white; margin-bottom: 1rem; font-weight: 700;">
        👶 DaycareMoments
    </h1>
    <p style="font-size: clamp(1rem, 3vw, 1.3rem); color: rgba(255,255,255,0.95); margin-bottom: 2rem; line-height: 1.6;">
        AI-Powered Photo Sharing Platform for Daycares
    </p>
</div>
""", unsafe_allow_html=True)

# Check if user is logged in
if 'user_id' in st.session_state:
    st.success(f"Welcome back, {st.session_state.get('first_name', 'User')}!")
    st.info("Use the sidebar to navigate to your dashboard")
else:
    st.info("👈 Please login or register using the sidebar to get started")

st.divider()

# Feature highlights
st.subheader("✨ Key Features")

# Use responsive columns that stack on mobile
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    st.markdown("### 📸 Smart Photos")
    st.write("AI-powered face recognition and instant child tagging")

with col2:
    st.markdown("### 💬 AI Assistant")
    st.write("Chat to find photos and get daily summaries")

with col3:
    st.markdown("### 📞 Voice Calls")
    st.write("24/7 AI agent via phone")

st.divider()

# Simple stats
st.subheader("📊 Platform")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Photos", "12,450")
with col2:
    st.metric("Daycares", "45")
with col3:
    st.metric("Parents", "892")
with col4:
    st.metric("Children", "1,234")

st.divider()

# Simple how it works
st.subheader("🔄 How It Works")
col1, col2 = st.columns(2)

with col1:
    st.markdown("**For Parents:**")
    st.write("1. Login to your account")
    st.write("2. View daily photos")
    st.write("3. Chat with AI assistant")
    st.write("4. Download photos")

with col2:
    st.markdown("**For Staff:**")
    st.write("1. Upload photos")
    st.write("2. AI auto-tags children")
    st.write("3. Approve & share")
    st.write("4. View analytics")

st.divider()

# Pricing
st.subheader("💰 Pricing")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**Free**")
    st.write("50 children")
    st.write("100 photos/month")
    st.write("**$0/month**")

with col2:
    st.markdown("**Starter**")
    st.write("100 children")
    st.write("500 photos/month")
    st.write("**$29/month**")

with col3:
    st.markdown("**Professional**")
    st.write("Unlimited")
    st.write("All features")
    st.write("**$99/month**")

st.divider()

# Footer
st.markdown("Made with ❤️ for daycares and parents | © 2025 DaycareMoments")
