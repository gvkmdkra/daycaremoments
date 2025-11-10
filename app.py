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

# Hero Section with Animated Gradient
st.markdown("""
<div style="
    background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
    border-radius: 30px;
    padding: 3rem 2rem;
    text-align: center;
    backdrop-filter: blur(10px);
    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
    margin-bottom: 2rem;
    animation: float 3s ease-in-out infinite;
">
    <div style="font-size: 5rem; margin-bottom: 1rem; animation: bounce 2s ease-in-out infinite;">👶</div>
    <h1 style="
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #ffffff 0%, #f0f0f0 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 20px rgba(0,0,0,0.3);
    ">DaycareMoments</h1>
    <p style="
        font-size: 1.5rem;
        color: #ffffff;
        font-weight: 300;
        margin-bottom: 2rem;
        text-shadow: 1px 1px 10px rgba(0,0,0,0.5);
    ">✨ Capture Every Precious Moment with AI-Powered Intelligence ✨</p>
    <p style="
        font-size: 1.1rem;
        color: rgba(255,255,255,0.9);
        max-width: 800px;
        margin: 0 auto 2rem auto;
        line-height: 1.8;
    ">
        The revolutionary platform connecting daycares and parents through smart photo sharing,
        real-time AI assistance, and seamless communication. Watch your child's day unfold,
        powered by cutting-edge facial recognition and intelligent automation.
    </p>
</div>

<style>
@keyframes float {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-20px); }
}
@keyframes bounce {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.1); }
}
@media (max-width: 768px) {
    div h1 { font-size: 2rem !important; }
    div p { font-size: 1rem !important; }
    div div { font-size: 3rem !important; }
}
</style>
""", unsafe_allow_html=True)

# Check if user is logged in
if 'user_id' in st.session_state:
    st.success(f"🎉 Welcome back, {st.session_state.get('first_name', 'User')}! Your dashboard awaits.")
    st.info("👈 Navigate to your personalized dashboard using the sidebar")
else:
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #38ef7d 0%, #11998e 100%);
        border-radius: 20px;
        padding: 1.5rem;
        text-align: center;
        color: white;
        font-size: 1.2rem;
        font-weight: 600;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        margin-bottom: 2rem;
    ">
        👈 <strong>Get Started Now!</strong> Login or register using the sidebar to experience the magic
    </div>
    """, unsafe_allow_html=True)

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
