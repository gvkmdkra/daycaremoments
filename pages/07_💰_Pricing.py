"""Pricing and Subscription Management"""

import streamlit as st
from app.utils.auth import get_current_user
from app.database import get_db
from app.database.models import Subscription, Daycare
from app.config import Config
from datetime import datetime, timedelta
import uuid
from app.utils.ui_theme import apply_professional_theme

st.set_page_config(page_title="Pricing", page_icon="💰", layout="wide")

# Apply professional theme
apply_professional_theme()

st.title("💰 Pricing Plans")
st.write("Choose the perfect plan for your daycare")

# Get current user (if logged in)
try:
    user = get_current_user()
    is_logged_in = True
except:
    user = None
    is_logged_in = False

# ===== PRICING TIERS =====
st.divider()

col1, col2, col3, col4 = st.columns(4)

# FREE TIER
with col1:
    st.markdown("""
    <div style="border: 2px solid #4CAF50; border-radius: 10px; padding: 20px; text-align: center;">
        <h3>🌱 Free</h3>
        <h2>$0</h2>
        <p>per month</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    **Perfect for:**
    - Small home daycares
    - Getting started
    - Testing the platform

    **Features:**
    - ✅ Up to 10 children
    - ✅ 100 photos/month
    - ✅ Basic photo sharing
    - ✅ Parent notifications
    - ✅ Mobile access
    - ✅ Email support
    - ❌ Face recognition
    - ❌ AI chat
    - ❌ Voice calling
    - ❌ Advanced analytics
    """)

    if st.button("Get Started Free", key="free_plan", use_container_width=True):
        if is_logged_in:
            st.info("You're already on the Free plan! Upgrade anytime.")
        else:
            st.switch_page("pages/01_🔐_Login.py")

# STARTER TIER
with col2:
    st.markdown("""
    <div style="border: 2px solid #2196F3; border-radius: 10px; padding: 20px; text-align: center;">
        <h3>🚀 Starter</h3>
        <h2>$29</h2>
        <p>per month</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    **Perfect for:**
    - Growing daycares
    - 10-30 children
    - Professional features

    **Features:**
    - ✅ Up to 30 children
    - ✅ 500 photos/month
    - ✅ **Face recognition**
    - ✅ **AI chat assistant**
    - ✅ Auto photo tagging
    - ✅ Activity logging
    - ✅ Email & SMS alerts
    - ✅ Basic analytics
    - ✅ Priority support
    - ❌ Voice calling
    - ❌ Advanced analytics
    - ❌ Custom branding
    """)

    if st.button("Start 14-Day Trial", key="starter_plan", use_container_width=True):
        handle_subscription("starter", 29)

# PRO TIER
with col3:
    st.markdown("""
    <div style="border: 2px solid #FF9800; border-radius: 10px; padding: 20px; text-align: center; background-color: #FFF3E0;">
        <h3>⭐ Pro</h3>
        <h4>MOST POPULAR</h4>
        <h2>$79</h2>
        <p>per month</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    **Perfect for:**
    - Established daycares
    - 30-100 children
    - Full feature set

    **Features:**
    - ✅ Up to 100 children
    - ✅ Unlimited photos
    - ✅ **Face recognition**
    - ✅ **AI chat assistant**
    - ✅ **Voice calling agent**
    - ✅ **Advanced analytics**
    - ✅ Auto photo tagging
    - ✅ Activity logging
    - ✅ Email & SMS alerts
    - ✅ Custom branding
    - ✅ API access
    - ✅ Dedicated support
    - ✅ 99.9% uptime SLA
    """)

    if st.button("Start 14-Day Trial", key="pro_plan", use_container_width=True):
        handle_subscription("pro", 79)

# ENTERPRISE TIER
with col4:
    st.markdown("""
    <div style="border: 2px solid #9C27B0; border-radius: 10px; padding: 20px; text-align: center;">
        <h3>🏢 Enterprise</h3>
        <h2>Custom</h2>
        <p>contact us</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    **Perfect for:**
    - Large organizations
    - Multiple locations
    - Custom requirements

    **Features:**
    - ✅ Unlimited children
    - ✅ Unlimited photos
    - ✅ **All Pro features**
    - ✅ Multi-location support
    - ✅ Custom integrations
    - ✅ Dedicated account manager
    - ✅ Custom SLA
    - ✅ Training & onboarding
    - ✅ White-label option
    - ✅ On-premise deployment
    - ✅ Advanced security
    - ✅ Compliance support
    """)

    if st.button("Contact Sales", key="enterprise_plan", use_container_width=True):
        st.info("📧 Email: sales@daycaremoments.com")
        st.info("📞 Phone: 1-800-DAYCARE")

st.divider()

# ===== FEATURE COMPARISON TABLE =====
st.subheader("📊 Feature Comparison")

comparison_data = {
    "Feature": [
        "Children Limit",
        "Photos per Month",
        "Photo Storage",
        "Face Recognition",
        "AI Chat Assistant",
        "Voice Calling Agent",
        "Activity Logging",
        "Parent Notifications",
        "Email & SMS Alerts",
        "Analytics Dashboard",
        "Custom Branding",
        "API Access",
        "Mobile App",
        "Support Level",
        "Uptime SLA",
        "Price per Month"
    ],
    "🌱 Free": [
        "10", "100", "1 GB", "❌", "❌", "❌", "✅", "✅", "Email only",
        "Basic", "❌", "❌", "✅", "Email", "99%", "$0"
    ],
    "🚀 Starter": [
        "30", "500", "10 GB", "✅", "✅", "❌", "✅", "✅", "✅",
        "Basic", "❌", "❌", "✅", "Priority", "99.5%", "$29"
    ],
    "⭐ Pro": [
        "100", "Unlimited", "100 GB", "✅", "✅", "✅", "✅", "✅", "✅",
        "Advanced", "✅", "✅", "✅", "Dedicated", "99.9%", "$79"
    ],
    "🏢 Enterprise": [
        "Unlimited", "Unlimited", "Unlimited", "✅", "✅", "✅", "✅", "✅", "✅",
        "Custom", "✅", "✅", "✅", "24/7", "Custom", "Custom"
    ]
}

st.table(comparison_data)

st.divider()

# ===== CURRENT SUBSCRIPTION (if logged in) =====
if is_logged_in and user:
    st.subheader("📋 Your Current Subscription")

    with get_db() as db:
        subscription = db.query(Subscription).filter(Subscription.daycare_id == user.daycare_id).first()
        daycare = db.query(Daycare).filter(Daycare.id == user.daycare_id).first()

    if subscription:
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Current Plan", subscription.plan_name.title())
        with col2:
            st.metric("Status", subscription.status.title())
        with col3:
            st.metric("Price", f"${subscription.price}/month")

        st.write(f"**Daycare:** {daycare.name}")
        st.write(f"**Billing Cycle:** {subscription.billing_cycle}")

        if subscription.trial_end_date:
            days_left = (subscription.trial_end_date.date() - datetime.now().date()).days
            if days_left > 0:
                st.info(f"🎁 Trial ends in {days_left} days ({subscription.trial_end_date.strftime('%B %d, %Y')})")

        if subscription.next_billing_date:
            st.write(f"**Next Billing:** {subscription.next_billing_date.strftime('%B %d, %Y')}")

        st.divider()

        # Upgrade/downgrade options
        col1, col2 = st.columns(2)

        with col1:
            if st.button("⬆️ Upgrade Plan", use_container_width=True):
                st.info("Select a plan above to upgrade")

        with col2:
            if st.button("❌ Cancel Subscription", use_container_width=True):
                st.warning("Are you sure? Your subscription will remain active until the end of the billing period.")
                if st.button("Confirm Cancellation"):
                    with get_db() as db:
                        sub = db.query(Subscription).filter(Subscription.daycare_id == user.daycare_id).first()
                        sub.status = "cancelled"
                    st.success("Subscription cancelled. You can reactivate anytime.")
                    st.rerun()

    else:
        st.info("You don't have an active subscription. Choose a plan above to get started!")

st.divider()

# ===== FAQ =====
st.subheader("❓ Frequently Asked Questions")

with st.expander("What payment methods do you accept?"):
    st.write("""
    We accept all major credit cards (Visa, Mastercard, American Express, Discover)
    and ACH bank transfers for annual plans. All payments are processed securely through Stripe.
    """)

with st.expander("Can I change plans anytime?"):
    st.write("""
    Yes! You can upgrade or downgrade your plan at any time. When upgrading, you'll be charged
    the prorated difference immediately. When downgrading, the change takes effect at the start
    of your next billing cycle.
    """)

with st.expander("What happens to my data if I cancel?"):
    st.write("""
    Your data is retained for 90 days after cancellation, giving you time to export everything.
    After 90 days, all data is permanently deleted. You can export your photos and data anytime
    from the admin panel.
    """)

with st.expander("Is there a setup fee?"):
    st.write("""
    No setup fees! All plans include free onboarding, training materials, and email support.
    Pro and Enterprise plans include personalized onboarding sessions.
    """)

with st.expander("Do you offer annual billing?"):
    st.write("""
    Yes! Save 20% with annual billing:
    - Starter: $279/year (save $69)
    - Pro: $759/year (save $189)

    Contact sales for Enterprise annual pricing.
    """)

with st.expander("What about data security and privacy?"):
    st.write("""
    We take security seriously:
    - End-to-end encryption for all photos
    - SOC 2 Type II compliant
    - GDPR and CCPA compliant
    - Regular security audits
    - 99.9% uptime guarantee (Pro+)
    - Daily backups
    """)

with st.expander("Can I try before I buy?"):
    st.write("""
    Absolutely! We offer:
    - **Free plan**: Forever free, no credit card required
    - **14-day trial**: Full access to paid features
    - **Demo available**: Schedule a personalized demo
    - **Money-back guarantee**: 30 days, no questions asked
    """)

st.divider()

# ===== TESTIMONIALS =====
st.subheader("💬 What Our Customers Say")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    > "DaycareMoments has transformed how we share photos with parents. The face recognition
    > saves us hours every week!"
    >
    > **- Sarah M., Little Learners Daycare**
    """)

with col2:
    st.markdown("""
    > "Parents love the AI chat feature. They can check on their kids anytime without
    > calling us during busy hours."
    >
    > **- Mike R., Sunshine Kids Care**
    """)

with col3:
    st.markdown("""
    > "The voice calling agent is incredible. Parents can get updates hands-free while
    > driving home from work."
    >
    > **- Jessica L., Happy Hearts Preschool**
    """)

st.divider()

# ===== CTA =====
st.markdown("""
<div style="text-align: center; padding: 40px; background-color: #E3F2FD; border-radius: 10px;">
    <h2>Ready to Get Started?</h2>
    <p style="font-size: 18px;">Join hundreds of daycares using DaycareMoments to delight parents!</p>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    if not is_logged_in:
        if st.button("🚀 Start Free Trial", use_container_width=True, type="primary"):
            st.switch_page("pages/01_🔐_Login.py")

# Helper function for subscription handling
def handle_subscription(plan_name: str, price: int):
    """Handle subscription creation/upgrade"""

    if not is_logged_in:
        st.info("Please log in or create an account to subscribe")
        if st.button("Go to Login"):
            st.switch_page("pages/01_🔐_Login.py")
        return

    # Check if Stripe is configured
    if not Config.STRIPE_SECRET_KEY:
        st.warning("⚠️ Payment processing is not configured yet.")
        st.info("""
        To enable payments, add your Stripe keys to the .env file:

        ```
        STRIPE_SECRET_KEY=sk_test_...
        STRIPE_PUBLISHABLE_KEY=pk_test_...
        ```

        For now, your subscription will be created in trial mode.
        """)

    # Create or update subscription
    with get_db() as db:
        existing_sub = db.query(Subscription).filter(Subscription.daycare_id == user.daycare_id).first()

        if existing_sub:
            # Update existing
            existing_sub.plan_name = plan_name
            existing_sub.price = price
            existing_sub.status = "trial" if not Config.STRIPE_SECRET_KEY else "active"
            existing_sub.trial_end_date = datetime.now() + timedelta(days=14)
            existing_sub.next_billing_date = datetime.now() + timedelta(days=14)

            st.success(f"✅ Upgraded to {plan_name.title()} plan!")

        else:
            # Create new
            new_sub = Subscription(
                id=str(uuid.uuid4()),
                daycare_id=user.daycare_id,
                plan_name=plan_name,
                status="trial",
                price=price,
                billing_cycle="monthly",
                trial_end_date=datetime.now() + timedelta(days=14),
                next_billing_date=datetime.now() + timedelta(days=14),
                created_at=datetime.utcnow()
            )
            db.add(new_sub)

            st.success(f"✅ Started 14-day trial of {plan_name.title()} plan!")

        st.balloons()
        st.rerun()
